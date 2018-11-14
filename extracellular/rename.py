import os

def rename(directory):

    for filename in os.listdir(directory):
        prefix = 'image_'
        filepath = os.path.join(directory, filename)
        filename_extension = os.path.splitext(filename)[1]
        filename_raw = os.path.splitext(filename)[0]
        new_filename = prefix + str(int(filename_raw)) + filename_extension
        #new_filename = filename.split('_')[1]
        new_filepath = os.path.join(directory, new_filename)
        os.rename(filepath, new_filepath)

def main():

    rename('./sample/CameraRGB')
    rename('./sample/CameraSemanticSegmentationVisualization')

if __name__ == '__main__':
    
    main()