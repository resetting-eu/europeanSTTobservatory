import os, shutil

total_files = 0


def get_total_files_in_a_directory(directory):
    global total_files
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
    return total_files


def get_randomised_sample(directory, sample_size):
    import random
    random.seed(42)
    randomised_sample = random.sample(os.listdir(directory), sample_size)
    return randomised_sample


def copy_files_to_randomisedSample_folder(directory, randomised_sample):
    for file in randomised_sample:
        shutil.copy(f"{directory}/{file}", "RandomisedSample")


def main():
    spain_dir = "Spain"
    scottish_dir = "Scotland"
    ue_dir = "UE"

    get_total_files_in_a_directory(spain_dir), get_total_files_in_a_directory(
        scottish_dir), get_total_files_in_a_directory(ue_dir)
    print(f"Total files: {total_files}")

    sample_size_per_catalogue = int(total_files * 0.05 / 3)
    print(f"Sample size: {sample_size_per_catalogue}")

    copy_files_to_randomisedSample_folder(spain_dir, get_randomised_sample(spain_dir, sample_size_per_catalogue))
    copy_files_to_randomisedSample_folder(scottish_dir, get_randomised_sample(scottish_dir, sample_size_per_catalogue))
    copy_files_to_randomisedSample_folder(ue_dir, get_randomised_sample(ue_dir, sample_size_per_catalogue))


main()
