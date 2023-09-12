from .base_model import BaseModel
from .networks import WaveNetModel as WaveNet
import torch.nn.functional as F
import torch
from . import networks
import random

class AdvWaveNetModel(BaseModel):

    def __init__(self, opt):
        super().__init__(opt)
        self.loss_names = ['ce','gen','disc']
        self.metric_names = ['accuracy']
        self.module_names = ['']  # changed from 'model_names'
        self.schedulers = []
        self.opt = opt
        
        # generator net
        self.net = WaveNet(layers=opt.layers,
                           blocks=opt.blocks,
                           dilation_channels=opt.dilation_channels,
                           residual_channels=opt.residual_channels,
                           skip_channels=opt.skip_channels,
                           end_channels=opt.end_channels,
                           input_channels=opt.input_channels,
                           output_length=opt.output_length,
                           output_channels=opt.output_channels,
                           num_classes=opt.num_classes,
                           kernel_size=opt.kernel_size,
                           bias=opt.bias)

        # discriminator net
        self.discriminator = WaveNet(layers=opt.layers,
                                    blocks=opt.blocks,
                                    dilation_channels=opt.dilation_channels//4,
                                    residual_channels=opt.residual_channels//2,
                                    skip_channels=opt.skip_channels//2,
                                    end_channels=opt.end_channels//4,
                                    input_channels=opt.input_channels,
                                    output_length=1,
                                    output_channels=1,
                                    num_classes=1,
                                    #dropout_p=opt.dropout_p,
                                    dropout_p=0.0,
                                    kernel_size=opt.kernel_size,
                                    bias=opt.bias)

        # this is normally done in base class, but it doesn't do it for the discriminator net so we do it here
        if self.gpu_ids:
            self.discriminator = networks.init_net(self.discriminator, self.opt.init_type, self.opt.init_gain,
                                self.opt.gpu_ids)  # takes care of pushing net to cuda
            assert torch.cuda.is_available()

        # optimizers for the parameters of the generator and the discriminator
        self.gen_optimizers = [torch.optim.Adam([
            {'params': [param for name, param in self.net.named_parameters() if name[-4:] == 'bias'],
             'lr': 2 * opt.learning_rate},  # bias parameters change quicker - no weight decay is applied
            {'params': [param for name, param in self.net.named_parameters() if name[-4:] != 'bias'],
             'lr': opt.learning_rate, 'weight_decay': opt.weight_decay}  # filter parameters have weight decay
        ])]
        self.disc_optimizers = [torch.optim.Adam([
        {'params': [param for name, param in self.discriminator.named_parameters() if name[-4:] == 'bias'],
            'lr': 2 * opt.learning_rate},  # bias parameters change quicker - no weight decay is applied
        {'params': [param for name, param in self.discriminator.named_parameters() if name[-4:] != 'bias'],
        'lr': opt.learning_rate, 'weight_decay': opt.weight_decay}  # filter parameters have weight decay
        ])]

        self.optimizers = self.gen_optimizers + self.disc_optimizers
        self.loss_ce = 0
        self.loss_gen = 0
        self.loss_disc = 0

#    def update_learning_rate(self):
#        for scheduler in self.schedulers:
#            scheduler.step()
#        lr = self.gen_optimizers[0].param_groups[0]['lr']
#        print('learning rate = %.7f' % lr)


    def name(self):
        return "AdvWaveNet"

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser.add_argument('--layers', type=int, default=10, help="Number of layers in each block")
        parser.add_argument('--blocks', type=int, default=4, help="Number of residual blocks in network")
        parser.add_argument('--dilation_channels', type=int, default=32, help="Number of channels in dilated convolutions")
        parser.add_argument('--residual_channels', type=int, default=32, help="Number of channels in the residual link")
        parser.add_argument('--skip_channels', type=int, default=256)
        parser.add_argument('--end_channels', type=int, default=256)
        parser.add_argument('--input_channels', type=int, default=(1+20))
        parser.add_argument('--output_length', type=int, default=1)
        parser.add_argument('--num_classes', type=int, default=20)
        parser.add_argument('--output_channels', type=int, default=(4*3))
        parser.add_argument('--kernel_size', type=int, default=2)
        parser.add_argument('--bias', action='store_false')
        parser.add_argument('--frequency_gen_updates', type=int, default=5)
        parser.add_argument('--dropout_p', type=float, default=0.5)
        parser.add_argument('--loss_ce_weight', type=float, default=1.0)
        return parser

    def set_input(self, data):
        # move multiple samples of the same song to the second dimension and the reshape to batch dimension
        input_ = data['input']
        target_ = data['target']
        input_shape = input_.shape
        target_shape = target_.shape
        # 0 batch dimension, 1 window dimension, 2 input channel dimension, 3 time dimension
        self.input = input_.reshape((input_shape[0]*input_shape[1], input_shape[2], input_shape[3])).to(self.device)
        #we collapse all the dimensions of target_ because that is the same way the output of the network is being processed for the cross entropy calculation (see self.forward)
        # here, 0 is the batch dimension, 1 is the window index, 2 is the time dimension, 3 is the output channel dimension
        self.target = target_.reshape((target_shape[0]*target_shape[1]*target_shape[2]*target_shape[3])).to(self.device)

    def forward(self,training_disc=False):
        #generator forward pass
        self.output = self.net.forward(self.input)
        x = self.output
        [n, channels, classes, l] = x.size() # l is number of time steps of output (which is opt.output_length)
        self.num_samples = n
        # reshape to get a sequence of logit vectors
        # note that if using reduced_state channels=1, while if using non-reduced_state, channel=12
        x = x.transpose(1, 3).contiguous()
        x = x.view(n * l * channels, classes)

        # cross entropy loss between prediction logits and target classes
        self.loss_ce = F.cross_entropy(x, self.target)

        # prediction accuracy
        self.metric_accuracy = (torch.argmax(x,1) == self.target).sum().float()/len(self.target)

        if training_disc:
            # convert logits to softmax
            # we omit the last output so that it corresponds to the same time points as the last l-1 song features 
            # and we reshape it to the right shape to feed as input to discriminator
            generated_level = F.softmax(self.output[:n//2,:,:,:-1],2).contiguous().view(n,channels*classes,l-1).cuda()
            
            # we concatenate the song features and the generated level before feeding to discriminator
            #print(generated_level[0,:,0])
            logits_gen = self.discriminator.forward(torch.cat((self.input[:n//2,:-self.opt.output_channels*self.opt.num_classes,-(l-1):],generated_level),1)).squeeze()
        else:
            
            # convert logits to softmax
            generated_level = F.softmax(self.output[:,:,:,:-1],2).contiguous().view(n,channels*classes,l-1).cuda()

            # we concatenate the song features and the generated level before feeding to discriminator
            logits_gen = self.discriminator.forward(torch.cat((self.input[:,:-self.opt.output_channels*self.opt.num_classes,-(l-1):],generated_level),1)).squeeze()

        p_gen = torch.sigmoid(logits_gen)
        # GAN generator loss
        self.loss_gen = torch.log(1-p_gen).mean() # high when discriminator thinks it likely false
        #lr = self.optimizers[0].param_groups[0]['lr'] # had this here in case I wanted to decay the loss_ce_weight..
        # add the cross entropy loss with given weighting
        self.loss_gen += self.opt.loss_ce_weight * self.loss_ce
        
        # TODO: should maybe also try generating some conditioned on emtpy inputs, as at the beginning of generation during testing..
        # Here is an idea of how to do it, do it on the dataset classes themselves, by appending zeros to the levels and song things
        #self.output = self.net.forward(torch.cat((torch.zeros(n,self.input.shape(1),receptive_field),self.input),2))

        #if training_disc:
        #    # convert logits to softmax
        #    # we omit the last output so that it corresponds to the same time points as the last l-1 song features 
        #    # and we reshape it to the right shape to feed as input to discriminator
        #    generated_level = F.softmax(self.output[:n//2,:,:,:receptive_field],2).contiguous().view(n,channels*classes,receptive_field).cuda()
        #    
        #    # we concatenate the song features and the generated level before feeding to discriminator
        #    logits_gen = self.discriminator.forward(torch.cat((self.input[:n//2,:-self.opt.output_channels*self.opt.num_classes,:receptive_field],generated_level),1)).squeeze()
        #else:
        #    
        #    # convert logits to softmax
        #    generated_level = F.softmax(self.output[:,:,:,:receptive_field],2).contiguous().view(n,channels*classes,l-1).cuda()

        #    # we concatenate the song features and the generated level before feeding to discriminator
        #    logits_gen = self.discriminator.forward(torch.cat((self.input[:,:-self.opt.output_channels*self.opt.num_classes,:receptive_field],generated_level),1)).squeeze()

    def forward_real(self):
        # discriminator forward pass for real song/block pairs 
        n = self.num_samples
        #self.forward()
        # p_real = self.discriminator.forward(self.input[:,-self.opt.output_channels*self.opt.num_classes:,:l]).squeeze()
        l = self.opt.output_length
        # smoothing the one-hot vectors into softmaxes (helps the generator, by making the real ones not so easy to identify for being one-hot)
        output_features = self.opt.output_channels*self.opt.num_classes
        softmax_beta = random.randint(2,7)
        level_features = self.input[n//2:,-output_features:,:l]
        shape = level_features.shape
        level_features = F.softmax(softmax_beta*level_features.view(shape[0],self.opt.output_channels,self.opt.num_classes,shape[2]),dim=2)
        level_features = level_features.contiguous().view(shape[0],output_features,shape[2])
        #print(level_features[0,:,0])
        smoothed_real = torch.cat((self.input[n//2:,:-output_features,:l],level_features),1)
        # we are feeding the first half of the batch to the discriminator and the second half to the generator, so that the generated and real inputs are uncorrelated
        # NOTE: this requires n_batches*n_windows > 1
        logits_real = self.discriminator.forward(smoothed_real).squeeze()
        p_real = torch.sigmoid(logits_real)
        # GAN discriminator loss
        self.loss_disc = -self.loss_gen - torch.log(p_real).mean()
        #self.loss_disc  += self.opt.loss_ce_weight * self.loss_ce

    def gen_backward(self):
        self.gen_optimizers[0].zero_grad()
        self.loss_gen.backward()
        self.gen_optimizers[0].step()

    def disc_backward(self):
        self.disc_optimizers[0].zero_grad()
        self.loss_disc.backward()
        self.disc_optimizers[0].step()

    def optimize_parameters(self,optimize_generator = False):
        self.set_requires_grad(self.net, requires_grad=True)
        self.forward()
        if optimize_generator:
            self.gen_backward()
        else:
            self.forward_real()
            self.disc_backward()
        for scheduler in self.schedulers:
            # step for schedulers that update after each iteration
            try:
                scheduler.batch_step()
            except AttributeError:
                pass
