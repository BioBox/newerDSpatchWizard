Newer Super Mario Bros. DS
Version: 1.16 (February 4, 2022)


================
1. Requirements
================

1. An untrimmed New Super Mario Bros. ROM (Japan, US, EUR, KOR,
   or CHN regions).
2. A computer running Windows XP or newer, macOS Sierra or newer, Linux,
   or a way to apply xdelta patches.
3. A way to play the ROM: DS flashcarts, emulators, etc.


================================
2. Tested devices and emulators
================================

Emulators:
----------
- DeSmuMe 0.9.11
  Works pretty much perfectly, but requires a hefty computer.
  Make sure dynamic recompilation is checked in the emulation settings.
  Later releases of DeSmuMe include an upscaling option, which might
  produce small graphical problems, especially during the credits.

- MelonDS 0.9.1
  Works with sound problems and slight slowdown at times.

- Medusa
  ROM worked on the first alpha release; does not anymore.

- DraStic for Android
  Works perfectly.

- OpenEmu for macOS
  Works perfectly.

- No$GBA 2.7+
  Works fine, but many graphical elements don't work -- 3D in
  particular. Not recommended for gameplay.

- Wii U Virtual Console ("HachiHachi")
  Support for this was added in Newer DS 1.14. Works fine, albeit with
  all the issues that DS Virtual Console titles on Wii U generally
  bring. You may want to adjust the emulator's brightness; by default,
  it's quite dark. It's in the emulator's configuration_cafe.json file,
  under "Brightness".

Flashcarts:
-----------
- Acekard 2.1/Acekard 2.1i
  Works perfectly on latest AKAIO.

- Supercard DSTWO
  Works mostly fine in "patch" mode. Slight graphical glitches or
  slowdown might occur, same as with the original game.

- R4
  Works perfectly with the latest Wood firmware.

- Other flashcarts will probably work as well, as long as they support
  New Super Mario Bros.

Other:
------
- TWLoader/SRLoader/TWiLightMenu++ with nds-bootstrap
  Seems to work fine with Mario Kart DS set as donor ROM; tested on
  TWiLightMenu++ v20.2.1 with nds-bootstrap v0.40.2.
  nds-bootstrap updates sometimes break the game, so if you experience
  problems on more recent releases, try downgrading to that version.
  Also ensure that the "DMA Card Read" setting is set to "Off".


============
3. Patching
============

To make a copy of Newer DS, you need a copy of a clean New Super Mario
Bros. ROM from any region. You're on your own to obtain one, via
whatever means are available to you.

After obtaining an .nds file of New Super Mario Bros., extract the
contents of the downloaded zip somewhere on your computer and run the
patcher program designated for your operating system. 

For Linux and macOS users: you will first need to install the latest
Python 3 release for your system, which will allow you to run the .py
script. After installing Python, run the following commands in a
terminal window to install other libraries (PyQt5 is required, xdelta3
is optional):

    python3 -m pip install PyQt5
    python3 -m pip install xdelta3

After this, you will be able to launch the patch_wizard.py script. (If
double-clicking the file doesn't work, run "python3 patch_wizard.py" in
a terminal window after navigating to patch_wizard.py's directory.)

Follow the instructions on-screen, and you should end up with a patched
NDS file.

If you're unable to run the program, look around for a way to apply
xdelta patches to files on your operating system. Get an md5 hash of
your ROM and apply the xdelta whose filename matches.


===================
4. Troubleshooting
===================

1. The game crashes at any point.
---------------------------------
If you're playing the game on any of the mentioned compatible
flashcarts, try to back up and format your SD card using the SD
Association's card formatter:
https://www.sdcard.org/downloads/formatter_4/.

If this does not fix your issue, please contact admin@newerteam.com,
preferably with a screenshot of the crash dump the game should produce.
Please include a detailed set of instructions on how to reproduce the
crash.

2. The game is slow!
--------------------
Generally, this means your computer is not powerful enough to run DS
emulators. Nevertheless, below follows a list of fixes.

- If using DeSmuMe, try to enable frameskipping under Config->Frame Skip
  and enable dynamic recompilation under Config->Emulation settings.
  If using DeSmuMe on Linux, you have to run the emulator with the
  "--cpu-mode=1" parameter from the terminal.

- If running on a Windows laptop, try to go into Maximum Performance
  mode, available in the battery settings. Be sure to have the computer
  plugged in, as well; otherwise, the CPU is throttled to conserve
  power.

- On DSTWO, try to enable the "clean" mode. You will need a regular,
  non-SDHC SD card for this, however, as the SDHC support for clean mode
  is shoddy.

3. The patcher says my ROM is unsupported!
------------------------------------------
Your ROM might be not a clean New Super Mario Bros. ROM, or you might
have not unpacked all the xdelta patches fom the .zip properly.

Please note that since 1.05, we have dropped support for trimmed ROMs,
and ROMs from regions other than Japan, Europe, America, Korea and China
have never been supported.


=============
5. Changelog
=============

1.16 (February 4, 2022)
    - Fixed some title screen logos.
    - Fixed rumble detection for some devices.
    - The patch wizard has been updated to version 1.03. It has various
      improvements and should work more reliably. Most notably, the
      patcher can now succeed even if the xdelta3 Python module is not
      installed and the bundled xdelta3.exe fails to run.

1.15 (June 18, 2021)
    - Fixed a midpoint-related bug in 8-2 introduced in version 1.14.

1.14 (May 30, 2021)
    - Newer DS will now work properly if injected into a Wii U Virtual
      Console title.
    - Moved the World 1 title screen stage from World 1-1 into its own
      slot.
    - 3-Ghost House: Changed 2nd star coin location, made some parts
      easier.
    - 3-Castle: Made a small portion before the checkpoint easier and
      less confusing.
    - 5-Ghost House: Fixed background scrolling.
    - 8-Castle: Fixed some tiling.
    - 8-Castle: Added lava to the final fight.
    - 6-4: Make everything generally less annoying.
    - 6-5: Add a second bouncy platform after the sliding section.
    - 7-Ghost House: Fixed a potential impossible-to-dodge hit by
      removing a Broozer.
    - 7-3: Made last Giant Spike Ball not despawn.
    - 7-3: Added Red ? Blocks and Hammer Bros. to the level.
    - Added Wii U testing section to credits.
    - Other miscellaneous fixes and changes.

1.13 (February 10, 2021)
    - In World 8-Castle, changed the final star coin.
    - Made World 7-2 easier in general.
    - Changed the way you bounce on Bouncy Clouds; they don't  require
      any button press timing anymore.
    - Changed crash screen colours.
    - Fixed uneven brightness on both screens. (Courtesy of GameratorT)
    - Removed a 1UP Mushroom from 1-1.
    - Fixed a potential Mini-Mushroom related softlock in 8-3.
    
1.12 (August 26, 2020)
    - Fixed an overlapping question block.

1.11 (May 31, 2020)
    - Adjusted level preview for 1-3 Snailicorn Grove.
    - Fixed level intro screen for 4-6 Grimoire Grounds.

1.10 (May 30, 2020)
    - Fixed secondary midpoint bug in World 5-Ghost House.
    - Fixed level preview for 4-6 Springy Spiritland.
    - Renamed Springy Spiritland to Grimoire Grounds.
    - Added Triple coin blocks to multiple levels.

1.07 (May 27, 2018)
    - Made 7-2 much easier.
    - Fixed midpoint appearing in midair in 5-Castle.
    - Fixed a camera bug in 5-B.
    - Fixed version being reported incorrectly.

1.06 (April 24, 2018)
    - Fixed an issue with Luigi's sound effects on the World Map.

1.05 (April 21, 2018)
    - Fixed a collision bug in 7-3.
    - Fixed a bug with Pokeys and Hammers.
    - Fixed a possible softlock in 8-3.
    - Fixed a camera issue in the 4-Ghost House.
    - Fixed a possible out-of-bounds in 5-Castle.
    - Fixed a possible out-of-bounds in 8-A.
    - Fixed a bug where tile animations would sometimes stop playing.
    - Fixed possible crash on level load.
    - Changed the way Rumble Paks are detected to hopefully support
      other types.
    - Fixed an entrance type in 1-1.
    - Changed the location of a block in 1-4.
    - Fixed a possibility of getting stuck by despawning a mushroom in
      8-A.
    - Fixed breaking pipes respawning once you got too far away in 2-2
      and 4-3.
    - Fixed a Koopa Troopa in 2-3 dancing on pipe joints.
    - Fixed a possible softlock in level 7-Tower, which could be
      achieved by using the vertical tilting lift.
    - Changed the timer of 7-Castle from 300 to 500.
    - Fixed a possibility of entering the warp in 8-Tanks without the
      pipe cannon.
    - Fixed a bug in 5-B with camera stopper range being set too high
    - Fixed a bug on the world map, where getting into the world select
      and opening up the menu at the same time caused a softlock.
    - Fixed a softlock in the Final Boss Battle caused by stomping
      Bowser Jr. too quickly.
    - Made 2-4 a bit easier by moving the camera all the way to the left
      and putting in indicative arrows.
    - Changed the position of 2-4's third star coin.
    - Fixed a camera glitch in 5-B.
    - Made it so it's possible to backtrack from the final star coin in
      5-B to the platform Koopas are on.
    - Fixed the level load screen, where selecting the player too
      quickly made the graphics jerk.
    - Fixed a bug in 3-B where you could get killed by the poison while
      on Dorrie if you stood in a specific spot at the beginning of the
      level.
    - Changed 8-6 so that it's possible to get the second star coin
      without an inventory powerup if starting from the midway point.
    - Removed upside down slopes from all underwater levels.
    - Removed two cheep cheeps from 3-A to prevent slowdown on real
      hardware.
    - Changed the sounds played on World 8 bridge reveal.
    - Other miscellaneous level changes.
    - Very minor changes to the Patch Wizard. (1.02)
    - Dropped support for patching trimmed ROMs.

1.04 (December 29, 2017)
    - Fixed an issue that could cause crashes on certain devices.

1.03 (December 28, 2017)
    - Updated the font used for "Time's Up!" to match that of similar
      messages.
    - Fixed certain sound effects cancelling the star coin cheer sound.
    - Fixed a collisions-related bug in the final castle.
    - Made the final area of the final castle slightly easier.
    - Extended autoscrolling in 2-A to fix a bug where the pipe would
      sometimes not appear in the first area.
    - Fixed a platform in World 7-1 sometimes not spawning.
    - Fixed a bug with Buzzy Beetles and the hammer suit.
    - Fixed a possible unfair kill in World 5-1.
    - Extended timers slightly in some World 1 levels.
    - Changed one of the entrance properties in 1-1.
    - Relaxed the timing for the final Star Coin in 2-4.
    - Changed Luigi's animation when holding things, and sped up his
      falling animation.
    - Changed a section of 2-4 to fix the minecart possibly crashing
      into the floor.
    - Changed other parts of 2-4 to prevent the minecart from going
      backwards through the level.
    - Fixed a small graphical mistake on level intro screens.
    - Fixed Thundercloud and Angry Sun being killable only once using
      hammers.
    - Miscellaneous level errors corrected.
    - Made the patch wizard more robust. (Updated to version 1.01.)

1.02 (December 26, 2017)
    - Fixed a memory leak.
    - Fixed the credits not starting.
    - Fixed a crash when touching the World 4 Bowser with a shell.
    - Miscellaneous level errors corrected.

1.01 (December 25, 2017)
    - Some players have reported a crash on the title screen after
      quitting from the map. We're unable to reproduce it, but we've
      implemented a possible fix.
    - If you quit without saving after launching a new game, the game
      would incorrectly place you in World 2 when reopening that file.
      This is fixed now.
    - Fixed a bug with Lakitus and hammers.
    - Changed the font for red coins.
    - Changed the email address displayed on the crash screen.
    - Fixed a tiling mistake in World 2-3

1.00 (December 25, 2017)
    Initial release
