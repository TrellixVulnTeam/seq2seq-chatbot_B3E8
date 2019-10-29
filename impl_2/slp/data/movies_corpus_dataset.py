import os

from zipfile import ZipFile

from torch.utils.data import Dataset

from slp.config.moviecorpus import MOVIECORPUS_URL
from slp.util.system import download_url


class MovieCorpusDataset(Dataset):
    def __init__(self, directory, transforms=None, train=True):
        dest = download_url(MOVIECORPUS_URL, directory)
        with ZipFile(dest, 'r') as zipfd:
            zipfd.extractall(directory)
        self._file_lines = os.path.join(directory, 'cornell '
                                                           'movie-dialogs '
                                                           'corpus',
                                        'movie_lines.txt')

        self._file_convs = os.path.join(directory, 'cornell '
                                                           'movie-dialogs '
                                                           'corpus',
                                        'movie_conversations.txt')

        self.transforms = transforms
        self.pairs = self.get_metadata()
        self.transforms = transforms

    def get_metadata(self):
        movie_lines = open(self._file_lines, encoding='utf-8',
                           errors='ignore').read().split('\n')
        movie_conv_lines = open(self._file_convs, encoding='utf-8',
                                errors='ignore').read().split('\n')

        # Create a dictionary to map each line's id with its text
        id2line = {}
        for line in movie_lines:
            _line = line.split(' +++$+++ ')
            if len(_line) == 5:
                id2line[_line[0]] = _line[4]

        # Create a list of all of the conversations lines ids.
        convs = []
        for line in movie_conv_lines[:-1]:
            _line = line.split(' +++$+++ ')[-1][1:-1]\
                .replace("'", "").replace(" ", "")
            convs.append(_line.split(','))

        # Sort the sentences into questions (inputs) and answers (targets)
        questions = []
        answers = []

        for conv in convs:
            for i in range(len(conv) - 1):
                questions.append(id2line[conv[i]])
                answers.append(id2line[conv[i + 1]])
        return list(zip(questions, answers))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        question, answer = self.pairs[idx]

        if self.transforms is not None:
            question = self.transforms(question)
            answer = self.transforms(answer)

        return question, answer


if __name__ == '__main__':
    data = MovieCorpusDataset('../../data/')

    print(len(data))
    print(data[5])
    print(data[5783])
