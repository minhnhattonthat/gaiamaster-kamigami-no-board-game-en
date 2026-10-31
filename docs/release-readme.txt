GaiaMaster: Kamigami no Board Game - English patch v{{version}}

Unofficial fan translation for PlayStation. Not affiliated with Capcom.
This archive contains a patch and this README only, never a game image.
Use your own legally obtained Japanese disc dump; do not distribute patched ROMs.

BASE DISC
Filename: {{base_name}}
Size: {{base_size}} bytes
CRC32: {{base_crc32}}
MD5: {{base_md5}}
SHA-1: {{base_sha1}}
These are the project's verified input hashes, not an online database claim.

PATCHING
Use xdelta3 with the original .bin as source and {{patch}} as patch:
  xdelta3 -d -s "{{base_name}}" "{{patch}}" "gaiamaster_en.bin"
Keep your original .cue and copy it alongside the output .bin, updating its
FILE line to reference "gaiamaster_en.bin". Preserve the track settings.
Open the updated .cue in your emulator. Do not apply the patch to a .cue or .chd.
Patched BIN CRC32: {{patched_crc32}}
Patched BIN SHA-1: {{patched_sha1}}

TRANSLATION STATUS
Dialogue / chapter introductions / endings: English
Menus / card names / rules / help / biographies: English
Graphics text / chapter cards / game over / credits: English
Weapon-list password entry: original functional kana alphabet and keys retained
Intro artwork reading LANDMASTER: original English artwork retained
Spoken Japanese audio: original audio retained (this is a text translation)

PLAYING AND KNOWN LIMITATIONS
Tested with this project's PCSX-Redux nightly 29954.20261029.10 and scph5500 BIOS.
Circle confirms; cross cancels. Cold boot the patched disc: old savestates carry
old code and VRAM and cannot validate this patch. Back up existing saves first.
Keyboard input was not manually tested; automated controller routes were tested.
Other emulators and original hardware have not been validated for this release.
No known blocking bugs remain in the reviewed routes. Report problems with a
screenshot and, if possible, a savestate and steps to reproduce:
https://github.com/minhnhattonthat/gaiamaster-kamigami-no-board-game-en/issues

CREDITS AND LICENCES
Original game, Japanese script, artwork and audio: Capcom and the original staff.
English translation and tools: this project's contributors (MIT).
Extensive AI assistance: Claude (Anthropic) and Codex (OpenAI).
Graphics labels use rendered pixels from SIL OFL fonts; font files and their
notices are in the source repository, documented in docs/fonts.md.
https://github.com/minhnhattonthat/gaiamaster-kamigami-no-board-game-en

MIT License (English translation, tools and project-drawn text font)
Copyright (c) 2026 minhnhattonthat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
