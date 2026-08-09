# stream_flavor_text.py -- Exercise 02 starter
#
# See INSTRUCTIONS.md for the full requirements, and Lesson 02
# (lessons/02-streaming-responses.md) for every piece of syntax needed.

import sys

import anthropic

client = anthropic.Anthropic()

# TODO 1: Read the quest line name from sys.argv[1], defaulting to
# "Side Quests" if no argument was given.
quest_line = None

# TODO 2: Open a streamed request (client.messages.stream(...)) asking
# for a 3-4 sentence, in-universe description of what `quest_line` is
# generally about. Pick a max_tokens value generous enough to comfortably
# fit that.

# TODO 3: Inside the `with` block, iterate stream.text_stream and print
# each piece with end="" and flush=True.

# TODO 4: After the loop (still inside the `with` block, or after it --
# get_final_message() works either way as long as the stream has been
# fully consumed), call stream.get_final_message() and print its
# stop_reason and usage.output_tokens.

# TODO 5: If stop_reason is "max_tokens", print a clear warning that the
# text was cut off.
