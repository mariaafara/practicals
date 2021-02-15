import argparse
import requests
import mysql.connector
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def pre_process_text(sentence, stopwords_):
    """Method that pre-processes a sentence.

    :param sentence: The input sentence.
    :param stopwords_: A set of stopwords.
    :return: Pre-processed sentence in a list of tokens format.
    """
    """
    steps:
     -lower case and strip the sentence
     -tokenize the sentence using nltk word tokenizer
     -only leave words that are not in the French stopwords and are alphabetic

    """
    word_tokens = word_tokenize(sentence.lower().strip())
    filtered_sentence = [word for word in word_tokens if
                         word not in stopwords_ and word.isalpha()]
    return filtered_sentence


def get_translations(sentence):
    """Method that gets the translation of the input sentence using the libretranslate open-source API.

    :param sentence: String of glossaries separated by comma.
    :return: List of translated glossaries.
    """
    json_data = {'q': sentence,
                 "source": "fr",
                 "target": "es",
                 "Content-Type": "application/json"}
    libretranslate_endpoint = "https://libretranslate.com/translate"
    response = requests.post(libretranslate_endpoint, json_data)
    result = response.json()
    return result['translatedText'].split(',')


def prepare_translation_table_data(glossaries, translations):
    """Method that prepare a list of tuples.

    :param glossaries: List of glossaries.
    :param translations: List of translations
    :return: List of glossary and translation tuples.
    """
    records_to_insert = []
    for glossary, translation in zip(glossaries, translations):
        records_to_insert.append((glossary, translation))
    return records_to_insert


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--db-host', type=str, dest='db_host',
                        help='MySQL db host')
    parser.add_argument('--db-name', type=str, dest='db_name', required=True,
                        help='MySQL db name')
    parser.add_argument('--db-user', type=str, dest='db_user', required=True,
                        help='MySQL db user')
    parser.add_argument('--db-pass', type=str, dest='db_pass', required=True,
                        help='MySQL db pass')
    parser.add_argument('--glossary-file', type=str, dest='glossary_file', required=True,
                        help='Glossary file path')
    parser.add_argument('--text-file', type=str, dest='text_file', required=True,
                        help='Text file path')
    parser.add_argument('--top-n', type=int, dest='top_n', required=True,
                        help='Top number of glossaries to translate')
    args = parser.parse_args()

    db_con = mysql.connector.connect(
        user=args.db_user,
        password=args.db_pass,
        host=args.db_host if args.db_host else "localhost",
        database=args.db_name
    )
    print("Connected with DB")
    # read a glossary from the text file, lower case it, strip the read line to avoid spaces at the ends then,
    # add the glossary as a key in a dictionary with a 0 frequency as a value.
    glossaries_frequencies = dict()
    with open(args.glossary_file, encoding="utf-8") as f:
        for line in f:
            glossary = line.lower().strip()
            glossaries_frequencies[glossary] = 0
    print("Glossaries are read and saved")
    # load unique french stopwords from NLTK
    stop_words = set(stopwords.words('french'))

    # read one line at a time from the input text file, pre-process it, iterate over each word in the pre-processed line
    # and increment the frequency of a found glossary
    with open(args.text_file, encoding="utf-8") as f:
        for line in f:
            word_tokens = pre_process_text(line, stop_words)
            for word in word_tokens:
                if word in glossaries_frequencies:
                    glossaries_frequencies[word] += 1
    print("Saved the frequency of each glossary in the input text")

    add_glossary = (
        "INSERT INTO frequencies "
        "(glossary, frequency) "
        "VALUES (%s, %s)"
    )

    cursor = db_con.cursor()

    # prepare records of tuples of a glossary and its corresponding frequency to insert into the DB
    # only insert those of which were found in the input text i.e their frequency >=1
    records_to_insert = []
    for glossary, frequency in glossaries_frequencies.items():
        if frequency:
            records_to_insert.append((glossary, frequency))

    # insert the found glossaries and their frequencies into frequencies table
    cursor.executemany(add_glossary, records_to_insert)
    db_con.commit()
    cursor.close()
    print("Inserted each occurred glossary and it's frequency in frequencies table")

    top_10_cmd = """
        SELECT glossary
        FROM frequencies
        ORDER BY frequency DESC
        LIMIT {}""".format(str(args.top_n))

    #  query the top n frequent glossaries in the database
    cursor = db_con.cursor()
    cursor.execute(top_10_cmd)
    top_n_glossaries = [record[0] for record in cursor.fetchall()]
    cursor.close()
    print("Selected top {} frequent glossaries from frequencies table".format(str(args.top_n)))

    # get the translations of the top 10 glossaries
    translations = get_translations(", ".join(top_n_glossaries))
    print("Translated the top {} glossaries ".format(str(args.top_n)))
    # map each glossary with its translation
    records_to_insert = prepare_translation_table_data(top_n_glossaries, translations)

    add_translation = (
        "INSERT INTO translations "
        "(glossary, spanish_translation) "
        "VALUES (%s, %s)"
    )

    # insert the top 10 glossaries and their translation into translation table
    cursor = db_con.cursor()
    cursor.executemany(add_translation, records_to_insert)
    db_con.commit()
    cursor.close()
    print("Inserted the top {} glossaries and their translation in translation table".format(str(args.top_n)))
    print("finish")