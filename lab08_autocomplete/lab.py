"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if type(key) != str:
            raise TypeError
        
        if key == "":
            self.value = value
            return

        if key[0] not in self.children:
            self.children[key[0]] = PrefixTree()

        self.children[key[0]][key[1:]] = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if type(key) != str:
            raise TypeError

        if key == "":
            if self.value == None:
                raise KeyError

            return self.value

        if key[0] not in self.children:
            raise KeyError

        return self.children[key[0]][key[1:]]

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if type(key) != str:
            raise TypeError

        if self[key] == None:
            raise KeyError
    
        self[key] = None

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if type(key) != str:
            raise TypeError

        if key == "":
            return self.value != None

        if key[0] not in self.children:
            return False

        return key[1:] in self.children[key[0]]

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        if self.value != None:
            yield ("", self.value)

        for k in self.children:
            for key, val in self.children[k]:
                yield (k + key, val)

    def get_tree(self, key):
        if type(key) != str:
            raise TypeError

        if key == "":
            return self

        if key[0] not in self.children:
            return None

        return self.children[key[0]].get_tree(key[1:])

def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    t = PrefixTree()
    m = {}

    sentences = tokenize_sentences(text)
    for sentence in sentences:
        for word in sentence.split(" "):
            m[word] = m.get(word, 0) + 1

    for k in m:
        t[k] = m[k]

    return t

def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if type(prefix) != str:
        raise TypeError

    start = tree.get_tree(prefix)
    if start == None:
        return []

    out = list(start)
    if max_count != None and len(out) > max_count:
        out.sort(key=lambda x: x[1])
        return [prefix+tup[0] for tup in out[(len(out)-max_count):]]
    else:
        return [prefix+tup[0] for tup in out]



def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    all_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    def rule1(word):
        out = set()
        for i in range(len(word)+1):
            for letter in all_letters:
                out.add(word[:i] + letter + word[i:])
        return out

    def rule2(word):
        out = set()
        for i in range(len(word)):
            out.add(word[:i] + word[i+1:])
        return out

    def rule3(word):
        out = set()
        for i in range(len(word)):
            for letter in all_letters:
                out.add(word[:i] + letter + word[i+1:])
        return out

    def rule4(word):
        out = set()
        for i in range(len(word)-1):
            out.add(word[:i] + word[i+1] + word[i] + word[i+2:])
        return out


    seen = set()
    
    # start by autocompleting the original prefix
    start_words = []
    main_start = tree.get_tree(prefix)
    if main_start != None:
        for tup in main_start:
            if prefix + tup[0] not in seen:
                seen.add(prefix + tup[0])
                start_words.append((prefix + tup[0], tup[1]))

    if max_count != None and len(start_words) >= max_count:
        start_words.sort(key=lambda x: x[1])
        return [tup[0] for tup in start_words[len(start_words)-max_count:]]

    # if we have more remaining space left, add the small edit words
    edit_words = []
    all_edits = rule1(prefix).union(rule2(prefix)).union(rule3(prefix)).union(rule4(prefix))
    for edit in all_edits:
        if (edit in tree) and (edit not in seen):
           seen.add(edit)
           edit_words.append((edit, tree[edit]))

    # truncate to max_count
    if max_count != None and len(start_words) + len(edit_words) > max_count:
        edit_words.sort(key=lambda x: (x[1]))
        return [tup[0] for tup in start_words + edit_words[(len(edit_words)+len(start_words)-max_count):]]
    else:
        return [tup[0] for tup in start_words + edit_words]



def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    # tokenizer
    parsed_pattern = []
    temp = ""
    for c in pattern:
        if c == "*":
            if temp != "":
                parsed_pattern.append(temp)
                temp = ""
            parsed_pattern.append("*")
        elif c == "?":
            if temp != "":
                parsed_pattern.append(temp)
                temp = ""
            parsed_pattern.append("?")
        else:
            temp += c
    if temp != "":
        parsed_pattern.append(temp)

    # recurse
    seen = set()
    out = []
    def r(tree, pattern_l, carry, star):
        if tree == None:
            return

        if pattern_l == []:
            if tree.value != None:
                out.append((carry, tree.value))
            if star:
                for tup in tree:
                    out.append((carry+tup[0], tup[1]))
            return

        if star:
            for child_tree in tree.children:
                if carry + child_tree not in seen:
                    seen.add(carry + child_tree)
                    r(tree.children[child_tree], pattern_l, carry + child_tree, True)

        if pattern_l[0] == "*":
            r(tree, pattern_l[1:], carry, True)
            for child_tree in tree.children:
                if carry + child_tree not in seen:
                    seen.add(carry + child_tree)
                    r(tree.children[child_tree], pattern_l[1:], carry + child_tree, True)
        elif pattern_l[0] == "?":
            for child_tree in tree.children:
                r(tree.children[child_tree], pattern_l[1:], carry + child_tree, False)
        else:
            r(tree.get_tree(pattern_l[0]), pattern_l[1:], carry + pattern_l[0], False)

    r(tree, parsed_pattern, "", False)
    return list(set(out))
    
    

# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
