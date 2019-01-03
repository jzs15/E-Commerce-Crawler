import re
import os
import bisect


class Segmentation:
    def __init__(self):
        print('init data')
        prob_cv = {}
        prob_v = {}
        word_all = []
        cur_path = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file_dict = os.path.join(cur_path, 'dict.txt')
        for line in open(file_dict, 'rb'):
            word, freq = line.split()
            freq = int(freq)
            word = str(word, 'utf-8')
            length = len(word)
            if not (length in prob_v):
                prob_v[length] = 0
            prob_v[length] += 1
            word_all.append(word)
            for i, char in enumerate(word):
                if not (char in prob_cv):
                    prob_cv[char] = {}
                if not (i in prob_cv[char]):
                    prob_cv[char][i] = 0
                prob_cv[char][i] += freq
        total_freq = sum(prob_v.values())
        for k, v in prob_v.items():
            prob_v[k] = float(v) / total_freq

        for k, v in prob_cv.items():
            subtotal_freq = sum(v.values())
            new_v = {}
            for kk, vv in v.items():
                new_v[kk] = float(vv) / subtotal_freq
            prob_cv[k] = new_v
        word_all.sort()
        self.prob_cv = prob_cv
        self.prob_v = prob_v
        self.word_all = word_all

    def has_prefix(self, word):
        idx = bisect.bisect_right(self.word_all, word)
        if idx < len(self.word_all):
            if self.word_all[idx].startswith(word) or self.word_all[idx - 1] == word:
                return True
        return False

    def in_dict(self, word):
        idx = bisect.bisect_right(self.word_all, word)
        if idx < len(self.word_all):
            if self.word_all[idx - 1] == word:
                return True
        return False

    def cut_sentence(self, string):
        length = len(string)
        if length < 2:
            return [string]
        i, j = 0, 1
        result = []
        while j < length:
            char = string[j]
            if not (char in self.prob_cv):
                self.prob_cv[char] = {}
            p1 = self.prob_v[j - i] * self.prob_cv[char].get(0, 0)
            p2 = self.prob_v[j - i + 1] * self.prob_cv[char].get(j - i, 0)
            part = string[i:j]
            if (p1 > p2) and self.in_dict(part):
                result.append(part)
                i = j
            else:
                if not self.has_prefix(string[i:j + 1]):
                    result.append(part)
                    i = j
            j += 1
            if j == length:
                result.append(string[i:])
        return result

    def cut(self, sentence):
        blocks = re.split(r'([^\u4E00-\u9FA5]+)', sentence)
        result = []
        for blk in blocks:
            if re.match(r'[\u4E00-\u9FA5]+', blk):
                result.extend(self.cut_sentence(blk))
            else:
                tmp = re.split(r'[^a-zA-Z0-9+#]', blk)
                result.extend([x for x in tmp if x.strip() != ''])
        return result


