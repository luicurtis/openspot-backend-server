import audio_rec.utils.libs.fingerprint as fingerprint
import numpy as np

from itertools import zip_longest
from termcolor import colored
from audio_rec.utils.libs.db_sqlite import SqliteDatabase
from audio_rec.utils.libs.reader_file import FileReader

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
        in zip_longest(fillvalue=fillvalue, *args))

def find_matches(samples, db, Fs=fingerprint.DEFAULT_FS):
    hashes = fingerprint.fingerprint(samples, Fs=Fs)
    return return_matches(hashes, db)

def return_matches(hashes, db):
    mapper = {}
    
    for hash, offset in hashes:
        mapper[hash.upper()] = 0
    values = mapper.keys()

    for split_values in grouper(values, 500):
        split_values_list = list(split_values)
        query = """
            SELECT upper(hash), song_fk, offset
            FROM fingerprints
            WHERE upper(hash) IN (%s)
        """
        query = query % ', '.join('?' * len(split_values_list))
        x = db.executeAll(query, split_values_list)
        matches_found = len(x)

        if matches_found > 0:
            msg = '   ** found %d hash matches (step %d/%d)'
            print (colored(msg, 'green') % (
                matches_found,
                len(split_values_list),
                len(values)
            ))
        else:
            msg = '   ** not matches found (step %d/%d)'
            print (colored(msg, 'red') % (
                len(split_values_list),
                len(values)
            ))

        for hash, sid, offset in x:
            val = (np.frombuffer(offset,int))
            yield (sid, val[0] - mapper[hash])


def align_matches(matches, db):
    diff_counter = {}
    largest = 0
    largest_count = 0
    song_id = -1

    for tup in matches:
        sid, diff = tup

        if diff not in diff_counter:
            diff_counter[diff] = {}

        if sid not in diff_counter[diff]:
            diff_counter[diff][sid] = 0

        diff_counter[diff][sid] += 1

        if diff_counter[diff][sid] > largest_count:
            largest = diff
            largest_count = diff_counter[diff][sid]
            song_id = sid 
    
    songM = db.get_song_by_id(song_id)

    nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                     fingerprint.DEFAULT_WINDOW_SIZE *
                     fingerprint.DEFAULT_OVERLAP_RATIO, 5)
    return {
        "SONG_ID" : song_id,
        "SONG_NAME" : songM[1],
        "CONFIDENCE" : largest_count,
        "OFFSET" : int(largest),
        "OFFSET_SECS" : nseconds
    }


def detect(filename):
    print("filename: %s", filename)
    song = None
    seconds = 5
    db = SqliteDatabase()

    r = FileReader(filename)
    res = r.parse_audio()
    file_hash = res['file_hash']
    print(file_hash)
    print(res)
    print(max(res['channels'][0]))

    chn = res['channels']
    matches = []
    for channel in chn:
        matches.extend(find_matches(channel, db))

    total_matches_found = len(matches)
    print(total_matches_found)
    if total_matches_found > 0:
        msg = ' ** totally found %d hash matches'
        print (colored(msg, 'green') % total_matches_found)

        song = align_matches(matches, db)

        msg = ' => song: %s (id=%d)\n'
        msg += '    offset: %d (%d secs)\n'
        msg += '    confidence: %d'

        print (colored(msg, 'green') % (
            song['SONG_NAME'], song['SONG_ID'],
            song['OFFSET'], song['OFFSET_SECS'],
            song['CONFIDENCE']
        ))
        return song['CONFIDENCE'], total_matches_found
    else:
        msg = ' ** not matches found at all'
        print (colored(msg, 'red'))
        return -1

# detect("media/uploads/audio_rec/caralarm2.mp3")