#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Description: Converts a segment of the YouTube transcript into SBV format and adjusts the start time

:Authors: (c) Artem Lutov <lav@lumais.com>
:Date: 2024-02-02
"""
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def timestamp(timeStr: str) -> float:
	"""Parse a timestamp in the following format: [[H:]M:]ss.ms

	Args:
		timeStr (str): textual timestamp

	Returns:
		float: timestamp

	>>> timestamp('12.25')
	12.25
	>>> timestamp('01:3:5.25')
	3785.25
	"""
	ts = 0.0  # Timestamp
	mul = 1  # Multiplier
	for t in reversed(timeStr.split(':')):
		ts += float(t) * mul
		mul *= 60
	return ts


def timestampStr(time: float) -> str:
	"""Convert float timestampt to the string format

	Args:
		time (float): float timestamp

	Returns:
		str: string timestamp

	>>> timestampStr(12.25) == '0:00:12.250'
	True
	>>> timestampStr(3785.25) == '1:03:05.250'
	True
	"""
	assert time >= 0, 'Non-negative time is expected: ' + str(time)
	ss = int(time)
	ms = int((time - ss) * 1000)
	mm, ss = divmod(ss, 60)
	h, mm = divmod(mm, 60)
	return f'{h}:{mm:0>2}:{ss:0>2}.{ms:0<3}'


def adjustSbv(finp, fout, ts: float):
	"""Adjust transcripts (tidy, and apply require transformations) and output them in the SBV format
	either in the [SBV format](https://docs.fileformat.com/settings/sbv/)
	or in the following raw format:
	```
	# Optional header comments

	m:ss
	Subtitle1
	Subtitle1 continuation

	h:mm:ss
	Subtitle2
	h:mm:ss
	Subtitle3
	```

	Args:
		finp (File): opened input file
		fout (File): opened output file
		ts (float): forced output start time

	Raises:
		RuntimeError
	"""
	isHdr = True  # Whether the header is processed
	hdrMark = '#'  # Header mark
	timeSep = ','  # Timestamp separator
	isSbv = None  # Whether the input format is SBV, raw, or has not been defined yet (None)
	times = []  # Start and finish timestamps for the accumulating captions
	captions = []  # A fragment of captions

	# Fetch first timestamp
	for ln in finp:
		# 1. Omit the header comments
		if isHdr and ln.startswith(hdrMark):
			continue
		isHdr = False
		# 2. Process subtitles
		toks = ln.split(maxsplit=1)
		# Omit empty lines
		if not toks:
			continue
		if len(toks) >= 2 or not toks[0][0].isdigit():
			# Aggregate subtitles
			captions.append(ln)
			continue
		# # Parse and correct the timings if necessary
		# if not ln[0].isdigit():
		# 	raise RuntimeError(f'Invalid format of the file: a timestamp is expected instead of "{tok}"')

		# 3. Fetch original timestamps
		# Identify the timestamp format and respective file format
		# Timestamp formats: [[H:]M:]ss.ms or 0:00:10.360,0:00:17.359
		timesNew = None
		if isSbv is None or isSbv:
			timesNew = [timestamp(s) for s in ln.split(timeSep)]
			if isSbv is None:
				assert not times, 'Timestampts should not be aggregated before their format is identified: ' + str(times)
				isSbv = len(timesNew) == 2
				# Update to to store offset of the first timestamp
				if ts is not None:
					ts = timesNew[0] - ts
				if not isSbv:
					times.append(timesNew[0] - (ts or 0))
			else:
				# Adjust timestamps
				assert len(times) == 2, 'Start and finish timestamps of the caption fragment should be already aggregated: ' + str(times)
				if ts is not None:
					for i in range(len(times)):
						times[i] -= ts
		else:
			# print(f'isSbv: {isSbv}, times: {times}')
			assert len(times) == 1, 'Non-SBV format of timestamps should have a single timestamp: ' + str(times)
			times.append(timestamp(ln) - (ts or 0))

		if captions:
			# Output timestamps and update them
			fout.write(timeSep.join(timestampStr(t) for t in times) + '\n')
			if isSbv:
				times = timesNew
			else:
				times.pop(0)
			# Output already accumulated captions
			captions.append('\n')
			fout.writelines(captions)
			captions.clear()
	# Output remaining captions with leading timestamps
	if captions:
		if len(times) == 1:
			times.append(times[0] + 5)  # Last caption let lasts 5 sec
		fout.write(timeSep.join(timestampStr(t) for t in times) + '\n')
		fout.writelines(captions)


if __name__ == '__main__':
	parser = ArgumentParser(description="""Transcript adjuster and converter to the
		[SBV](https://docs.fileformat.com/settings/sbv/) format from either SBV or raw format yielded by YouTube""",
		formatter_class=ArgumentDefaultsHelpFormatter,
		conflict_handler='resolve')
	parser.add_argument('inpfs', nargs='+', help='Input file names of the transcripts to be adjusted or converted')
	parser.add_argument('-s', '--start-time', type=str, default=None, help='Adjust start time of subtitles to the specified [[h:]m:]s.ms')
	parser.add_argument('-n', '--no-overwrites', action='store_true', help='Never overwrite the output file, omitting the processing if that case')
	inpfs = parser.parse_args().inpfs
	
	ts = None  # Required start time
	if parser.parse_args().start_time is not None:
		ts = timestamp(parser.parse_args().start_time)

	for ifname in inpfs:
		ofname, ext = os.path.splitext(ifname)
		if ext.lower() == '.sbv':
			ofname += '.fix'
		else:
			ext = '.sbv'
		ofname += ext
		if os.path.isfile(ofname):
			if parser.parse_args().no_overwrites:
				print('WARNING: the output file already exists, the processing is omitted: ' + ofname)
				continue
			else:
				print('WARNING: the output file already exists and will be overwritten: ' + ofname)
		with open(ifname, 'r') as finp:
			with open(ofname, 'w') as fout:
				adjustSbv(finp, fout, ts)
