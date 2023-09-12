# 슈퍼스타 리소스로 전처리된 데이터 셋 만들기

import os
from glob import glob
from ss_to_ds_json_converter import SSDSJsonConverter
from song_preprocessor import SongPreprocessor
UNIQUE_STATE_NAME = "ss_short"
OUTPUT_DIR = "../data/extracted_data/"+UNIQUE_STATE_NAME

if __name__ == '__main__':
    converter = SSDSJsonConverter()
    preprocessor = SongPreprocessor()
    level_path_list = ['Expert.dat', 'ExpertPlus.dat']
    game_dir_list = glob("../SuperStarResource/json/*")
    for game_dir in game_dir_list:

        json_path_list = glob(game_dir+"/*.json")
        for json_path in json_path_list:
            # 잘못된 이름 수정
            json_path.replace('-', '_')
            
            song_title = '_'.join(json_path.split('\\')[-1].split('_')[:-1])
            detail_dir = game_dir.split('\\')[-1].split('.')[0]+'_'+song_title # 게임 이름 + 음악 이름
            converter.set_output_path(OUTPUT_DIR+'/'+detail_dir)
            converter.convert(json_path)

        song_path_list = glob(game_dir+"/*.ogg")
        
        for song_path in song_path_list:
            # 잘못된 이름 수정
            song_path.replace('-', '_')

            song_title = song_path.split('\\')[-1].split('.')[0]
            detail_dir = game_dir.split('\\')[-1].split('.')[0]+'_'+song_title
            preprocessor.set_output_path(OUTPUT_DIR+'/'+detail_dir)
            preprocessor.copy_song_to_output(song_path)
            '''
            feature_path = preprocessor.preprocess(song_path)

            if not os.path.isfile(OUTPUT_DIR+'/'+detail_dir+'/'+level_path_list[0]):
                print('난이도 파일 없음 : '+detail_dir+'/'+level_path_list[0])
                continue
            for level_path in level_path_list:
                preprocessor.block_reduced(song_path, feature_path, OUTPUT_DIR+'/'+detail_dir+'/'+level_path)
            '''
        print(game_dir+'처리 완료!')