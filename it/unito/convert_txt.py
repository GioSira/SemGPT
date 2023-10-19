from glob import glob
import pickle

folder = f'/Users/128525/Desktop/Uni/SemGPT/it/unito/output/'

for file in glob(folder+'/**/*.bin', recursive=True):
        
        print(f'File: {file}')

        with open(file, 'rb') as reader: 
            res = pickle.load(reader)

            new_path = file.replace('.bin', '.txt').replace('output', 'output_txt').replace('\\', '/')
            #new_path = f'it/unito/output_txt/'
            with open(new_path, 'x', encoding="utf8") as writer:
                for k, v in res:
                    writer.write(f'{k} \n Expected: {v}\n')
                  
        