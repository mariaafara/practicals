import argparse
import mysql.connector


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Database tables')
    parser.add_argument('--db-host', type=str, dest='db_host',
                        help='MySQL db host')
    parser.add_argument('--db-name', type=str, dest='db_name', required=True,
                        help='MySQL db name')
    parser.add_argument('--db-user', type=str, dest='db_user', required=True,
                        help='MySQL db user')
    parser.add_argument('--db-pass', type=str, dest='db_pass', required=True,
                        help='MySQL db pass')
    args = parser.parse_args()
    
    db_con = mysql.connector.connect(
        user=args.db_user,
        password=args.db_pass,
        host=args.db_host if args.db_host else "localhost",
        database=args.db_name
    )
    frequencies_table = (
        "CREATE TABLE `frequencies` ("
        "  `glossary` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,"
        "  `frequency` INT NOT NULL,"
        "  PRIMARY KEY (`glossary`)"
        ") CHARSET=utf8"
    )
    translation_table = (
        "CREATE TABLE `translations` ("
        "  `glossary` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,"
        "  `spanish_translation` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,"
        "  PRIMARY KEY (`glossary`),"
        "  FOREIGN KEY (`glossary`)"
        " REFERENCES frequencies(glossary)"
        ") CHARSET=utf8"
    )
    # execute the queries
    cursor = db_con.cursor()
    cursor.execute(frequencies_table)
    print("frequencies table is created")
    cursor.execute(translation_table)
    print("translation table is created")
    db_con.commit()
    cursor.close()
    db_con.close()
    print("finish")