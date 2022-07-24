"""
Newer Super Mario Bros. DS Patch Wizard ("Newer DS Patch Wizard")
Copyright (C) 2017 RoadrunnerWMC, skawo

This file is part of Newer DS Patch Wizard.
"""
COPYRIGHT = """
Newer DS Patch Wizard is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Newer DS Patch Wizard is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Newer DS Patch Wizard.  If not, see <http://www.gnu.org/licenses/>.
"""
COPYRIGHT_HTML = """
Newer DS Patch Wizard is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
<br><br>
Newer DS Patch Wizard is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
<br><br>
You should have received a copy of the GNU General Public License
along with Newer DS Patch Wizard.  If not, see
<a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.
"""

PATCHER_VERSION = '1.03'


import enum
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

from PyQt5 import QtCore, QtGui, QtWidgets; Qt = QtCore.Qt

try:
    import xdelta3
except Exception:
    xdelta3 = None

import xdelta3_pure_py


WINDOW_TITLE = 'Newer Super Mario Bros. DS Patch Wizard'

WELCOME_HEADER = 'Welcome'
WELCOME_TEXT = """
Welcome to the <i>Newer Super Mario Bros. DS</i> Patch Wizard!
<br><br>

This wizard will help you prepare a copy of <i>Newer Super Mario Bros.
DS</i> using a copy of <i>New Super Mario Bros.</i> you already have.
<br><br>

Let's get started!
<br><br><br>

<small><i>
This program was written by <a href="http://newerteam.com">the Newer
Team</a>, which is not affiliated with Nintendo. Mario, Luigi, Yoshi,
and all related characters are © Nintendo, and are not under the
copyright of this program. All other copyrights are the property of
their respective owners.
<br><br>
""" + COPYRIGHT_HTML + """
</i></small>
<br>
<div align="right">
Patcher version """ + PATCHER_VERSION + """<br>
Game version GAME_VERSION<br>
<small>(these two versions need not match)</small><br>
</div>
""".replace('\n', ' ')

CHOOSE_ROM_HEADER = 'Select input ROM file'
CHOOSE_ROM_TEXT = """
Select your <i>New Super Mario Bros.</i> ROM file below.
If you don't have one, you'll need to get one before you can play
<i>Newer Super Mario Bros. DS</i>. The original ROM file won't be
overwritten or deleted, by default.
""".replace('\n', ' ')
CHOOSE_ROM_SELECT_TITLE = 'ROM file for <i>New Super Mario Bros.</i>:'
CHOOSE_ROM_SELECT = 'Choose...'
CHOOSE_ROM_PLACEHOLDER_TEXT = 'Press "Choose..." or type a file path here'
CHOOSE_ROM_DIALOG_TITLE = 'Select the ROM file for New Super Mario Bros.'
CHOOSE_ROM_DIALOG_FILTER = 'Nintendo DS ROM files (*.nds);;All files(*)'
a, b = '<small><span style="color:red;">', '</span></small>'
CHOOSE_ROM_STATUS_NONE = '<small>Please enter a file path.</small>'
CHOOSE_ROM_STATUS_NOT_FULL_PATH = (a + 'Please enter a full file path, '
    'not a relative one.' + b)
CHOOSE_ROM_STATUS_NONEXISTENT = a + "The file doesn't exist." + b
CHOOSE_ROM_STATUS_NOT_A_ROM = (a + "This doesn't seem to be a valid "
    'Nintendo DS ROM file.' + b)
CHOOSE_ROM_STATUS_UNIDENTIFIED = (a + "This doesn't seem to be a "
    '<i>New Super Mario Bros.</i> ROM file.' + b)
CHOOSE_ROM_STATUS_UNSUPPORTED = (a + "Unfortunately, this isn't a "
    'supported <i>New Super Mario Bros.</i> ROM file.' + b)

CHOOSE_OUTPUT_HEADER = 'Select output ROM file'
CHOOSE_OUTPUT_TEXT = """
Choose a file name for your copy of <i>Newer Super Mario Bros. DS</i>,
or leave it as the default to name it "Newer Super Mario Bros. DS.nds"
in the same folder as your <i>New Super Mario Bros.</i> ROM file.
""".replace('\n', ' ')
CHOOSE_OUTPUT_SELECT_TITLE = 'ROM file to save <i>Newer Super Mario Bros. DS</i> as:'
CHOOSE_OUTPUT_SELECT = 'Choose...'
CHOOSE_OUTPUT_PLACEHOLDER_TEXT = 'Press "Choose..." or type a file path here'
CHOOSE_OUTPUT_DIALOG_TITLE = 'Select a ROM file save location for Newer Super Mario Bros. DS'
CHOOSE_OUTPUT_DIALOG_FILTER = 'Nintendo DS ROM files (*.nds);;All files(*)'
CHOOSE_OUTPUT_STATUS_NONE = (a + 'Please enter a file path.' + b)
CHOOSE_OUTPUT_STATUS_INVALID = (a + "This doesn't seem to be a valid "
    'file path to save to.' + b)
CHOOSE_OUTPUT_STATUS_EXISTS = "<small>This file already exists.</small>"

CONFIRMATION_HEADER = 'Please confirm'
CONFIRMATION_TEXT = """
Make sure that everything below looks correct before clicking "Start."
""".replace('\n', '')
CONFIRMATION_BODY = """
<code style="font-family: monospace">[in-path]</code><br>
<br>
will be used to make a copy of <i>Newer Super Mario Bros. DS</i>, which
will be saved as<br>
<br>
<code style="font-family: monospace">[out-path]</code>
""".replace('\n', ' ')
CONFIRMATION_BUTTON_START = 'Start'

FINISHED_HEADER_SUCCESS = 'All done'
FINISHED_TEXT_SUCCESS = 'All done! We hope you enjoy the game.'
FINISHED_HEADER_FAILURE = 'Errors occurred'
FINISHED_TEXT_FAILURE = 'Some errors occurred during patching — please try again. If this error continues to occur, email the traceback below to admin@newerteam.com.'

NUM_PATCHES_REQUIRED = 10
ERROR_MISSING_FILES_TITLE = 'Missing files'
ERROR_MISSING_FILES_TEXT = 'Some required files seem to be missing. Please re-extract the zip file you downloaded and try again. If this continues to happen, redownload the zip file.'

del a, b


# He asked for it
# import getpass
# if getpass.getuser().lower() == 'naknow':
#     raise Exception('ERROR: Unknown error')



class RomFileStatus(enum.Enum):
    """
    The return type of classify_file(). Represents all possible scenarios
    for a given rom filename.
    """
    EMPTY            = 0  # Filename is empty or all whitespace
    NOT_FULL_PATH    = 1  # Filename is not complete (no slashes)
    NONEXISTENT      = 2  # No such file exists
    NOT_A_ROM        = 3  # File exists, but doesn't look like a DS rom
    UNIDENTIFIED_ROM = 4  # File is a DS rom, but not NSMB
    UNSUPPORTED_ROM  = 5  # File is a NSMB rom, but not one we can patch
    VALID_ROM        = 6  # File is a patchable NSMB rom




def file_md5(fn: Path) -> 'hashlib hash object':
    """
    Calculate the MD5 hash of the file with the given filename, using a
    method that is efficient even for large files.
    Return the hashlib hash object.
    """
    # https://stackoverflow.com/a/22058673

    BUF_SIZE = 65536

    md5 = hashlib.new('md5')

    with fn.open('rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5



def classify_file(fn: str) -> RomFileStatus:
    """
    Given a file path (string -- could be arbitrarily invalid as a file
    path), return a RomFileStatus representing whether or not it points
    to a patchable rom file.

    This function should run very quickly even for very large files.
    """
    if not fn.strip():
        return RomFileStatus.EMPTY

    try:
        fn = Path(fn)
    except Exception:
        return RomFileStatus.NONEXISTENT

    if not fn.is_absolute():
        return RomFileStatus.NOT_FULL_PATH

    if not fn.is_file():
        return RomFileStatus.NONEXISTENT

    with fn.open('rb') as f:
        first_200 = f.read(0x200)

    if len(first_200) < 0x200:
        # Unless it's "The Smallest NDS File"...
        return RomFileStatus.NOT_A_ROM

    # Padding area -- empty in all games I checked
    if any(first_200[0x15:0x1C]):
        return RomFileStatus.NOT_A_ROM

    # Check the Nintendo logo
    if (hashlib.sha256(first_200[0xC0:0x15D]).hexdigest() !=
            'a07b35ac13a40de9682fc24b4ded05b717da632fb621253e38cafec5471a1cce'):
        return RomFileStatus.NOT_A_ROM

    # Check for the NSMB rom name and game code (excluding region)
    if first_200[:15] != b'NEW MARIO\0\0\0A2D':
        return RomFileStatus.UNIDENTIFIED_ROM

    # If we made it this far, it's probably a NSMB rom.
    # Hash the whole file and check if it's one we have an xdelta for.
    xdelta_filename = Path('.') / 'data' / 'patches' / (file_md5(fn).hexdigest() + '.xdelta')
    if xdelta_filename.is_file():
        return RomFileStatus.VALID_ROM
    else:
        return RomFileStatus.UNSUPPORTED_ROM


def do_xdelta(base: bytes, patch: bytes) -> bytes:
    """
    Perform an xdelta patch using the best available technique.
    """
    # If the xdelta3 module is installed, use that
    if xdelta3 is not None:
        try:
            return xdelta3.decode(base, patch)
        except Exception:
            pass

    # Otherwise, try to run the xdelta3.exe program instead
    temp_base_fp = Path('.') / 'data' / 'temp1.bin'
    temp_patch_fp = Path('.') / 'data' / 'temp2.bin'
    temp_out_fp = Path('.') / 'data' / 'temp3.bin'
    temp_base_fp.write_bytes(base)
    temp_patch_fp.write_bytes(patch)

    try:
        command = ['xdelta3.exe', '-d', '-s', temp_base_fp.name, temp_patch_fp.name, temp_out_fp.name]
        if sys.platform == 'win32':
            subprocess.call(command, shell=True, cwd='data')
        else:
            # gulp
            command.insert(0, 'wine')
            subprocess.call(command, cwd='data')

        return temp_out_fp.read_bytes()

    except Exception:
        pass

    finally:
        temp_base_fp.unlink()
        temp_patch_fp.unlink()
        try:
            temp_out_fp.unlink()
        except Exception:
            pass

    # If that still didn't work, use the bundled pure-Python VCDIFF
    # implementation as a last resort
    out_file_obj = io.BytesIO()
    xdelta3_pure_py.apply_vcdiff(io.BytesIO(base), io.BytesIO(patch), out_file_obj)
    out_file_obj.seek(0)
    return out_file_obj.read()



def patch_rom_single(in_filepath: Path, out_filepath: Path) -> bytes:
    """
    The rest of the program exists as a fancy wrapper for this function.
    """
    original_rom = in_filepath.read_bytes()

    md5 = hashlib.md5(original_rom).hexdigest()

    xdelta_filename = Path('.') / 'data' / 'patches' / (md5 + '.xdelta')
    patch = xdelta_filename.read_bytes()

    newer_ds = do_xdelta(original_rom, patch)

    # Check that the patch was applied properly
    if hashlib.md5(newer_ds).hexdigest() != Info['outputHash']:
        raise RuntimeError('Patched output file is incorrect')

    out_filepath.write_bytes(newer_ds)  # yay

    # Check that the thing actually saved correctly
    if out_filepath.read_bytes() != newer_ds:
        raise RuntimeError('Unable to save to the output filepath specified')


def patch_rom(in_filepath: Path, out_filepath: Path) -> bytes:
    """
    Try to patch three times; if it still doesn't work, let the error
    propogate.
    """
    try:
        return patch_rom_single(in_filepath, out_filepath)
    except Exception:
        pass

    try:
        return patch_rom_single(in_filepath, out_filepath)
    except Exception:
        pass

    return patch_rom_single(in_filepath, out_filepath)



def create_welcome_page(wizard: QtWidgets.QWizard) -> QtWidgets.QWizardPage:
    """
    Create the welcome wizard page.
    """
    page = QtWidgets.QWizardPage(wizard)
    page.setTitle(WELCOME_HEADER)
    page.setMinimumHeight(350)  # fixes cut-off text on Windows 10

    # Welcome text label
    label = QtWidgets.QLabel(page)
    label.setWordWrap(True)
    label.setText(WELCOME_TEXT.replace('GAME_VERSION', Info['gameVersion']))

    # Layout
    L = QtWidgets.QVBoxLayout(page)
    L.addWidget(label)

    return page



class ChooseRomPage(QtWidgets.QWizardPage):
    """
    A wizard page that lets you choose an input rom file.
    """
    def __init__(self, wizard: QtWidgets.QWizard):
        super().__init__(wizard)
        self.setTitle(CHOOSE_ROM_HEADER)
        self.setSubTitle(CHOOSE_ROM_TEXT)

        # Selection label
        select_label = QtWidgets.QLabel(self)
        select_label.setWordWrap(True)
        select_label.setText(CHOOSE_ROM_SELECT_TITLE)

        # Select button
        select_btn = QtWidgets.QPushButton(self)
        select_btn.setText(CHOOSE_ROM_SELECT)
        select_btn.clicked.connect(self.select_btn_clicked)

        # Line edit
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.textChanged.connect(self.completeChanged)
        line_edit.setPlaceholderText(CHOOSE_ROM_PLACEHOLDER_TEXT)
        wizard.choose_rom_line_edit = line_edit

        # Status label
        status_label = QtWidgets.QLabel(self)
        status_label.setWordWrap(True)
        status_label.setText('')
        wizard.choose_rom_status_label = status_label

        # Layout
        selection_lyt = QtWidgets.QHBoxLayout()
        selection_lyt.addWidget(select_btn)
        selection_lyt.addWidget(line_edit)
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(select_label)
        L.addLayout(selection_lyt)
        L.addWidget(status_label)


    def select_btn_clicked(self):
        """
        The "Select" button was clicked.
        """
        fn = QtWidgets.QFileDialog.getOpenFileName(self,
            CHOOSE_ROM_DIALOG_TITLE,
            self.wizard().choose_rom_line_edit.text(),
            CHOOSE_ROM_DIALOG_FILTER)[0]
        if not fn: return

        self.wizard().choose_rom_line_edit.setText(fn)


    def isComplete(self):
        """
        Return True if a valid rom has been chosen, or False otherwise
        """
        result = classify_file(self.wizard().choose_rom_line_edit.text())

        bad_results = {
            RomFileStatus.EMPTY: CHOOSE_ROM_STATUS_NONE,
            RomFileStatus.NOT_FULL_PATH: CHOOSE_ROM_STATUS_NOT_FULL_PATH,
            RomFileStatus.NONEXISTENT: CHOOSE_ROM_STATUS_NONEXISTENT,
            RomFileStatus.NOT_A_ROM: CHOOSE_ROM_STATUS_NOT_A_ROM,
            RomFileStatus.UNIDENTIFIED_ROM: CHOOSE_ROM_STATUS_UNIDENTIFIED,
            RomFileStatus.UNSUPPORTED_ROM: CHOOSE_ROM_STATUS_UNSUPPORTED,
        }

        if result in bad_results:
            self.wizard().choose_rom_status_label.setText(bad_results[result])
            return False

        elif result == RomFileStatus.VALID_ROM:
            self.wizard().choose_rom_status_label.setText('')
            return True

        # Should never reach here
        self.wizard().choose_rom_status_label.setText('ERROR: UNKNOWN FILE STATUS')
        return False



class ChooseOutputPage(QtWidgets.QWizardPage):
    """
    A wizard page that lets you choose the output rom file.
    """
    def __init__(self, wizard: QtWidgets.QWizard):
        super().__init__(wizard)
        self.setTitle(CHOOSE_OUTPUT_HEADER)
        self.setSubTitle(CHOOSE_OUTPUT_TEXT)

        # Selection label
        select_label = QtWidgets.QLabel(self)
        select_label.setWordWrap(True)
        select_label.setText(CHOOSE_OUTPUT_SELECT_TITLE)

        # Folder-select button
        select_btn = QtWidgets.QPushButton(self)
        select_btn.setText(CHOOSE_OUTPUT_SELECT)
        select_btn.clicked.connect(self.select_btn_clicked)

        # Line edit
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.textChanged.connect(self.completeChanged)
        wizard.choose_output_line_edit = line_edit

        # Status label
        status_label = QtWidgets.QLabel(self)
        status_label.setWordWrap(True)
        status_label.setText('')
        wizard.choose_output_status_label = status_label

        # Layout
        selection_lyt = QtWidgets.QHBoxLayout()
        selection_lyt.addWidget(select_btn)
        selection_lyt.addWidget(line_edit)
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(select_label)
        L.addLayout(selection_lyt)
        L.addWidget(status_label)


    def initializePage(self) -> None:
        """
        Prepare the page based on input from previous pages.
        """
        initial_path = Path(self.wizard().choose_rom_line_edit.text()).parent
        initial_path /= 'Newer Super Mario Bros. DS.nds'
        self.wizard().choose_output_line_edit.setText(str(initial_path))


    def select_btn_clicked(self) -> None:
        """
        The "Select" button was clicked for the line edit.
        """
        fn = QtWidgets.QFileDialog.getSaveFileName(self,
            CHOOSE_OUTPUT_DIALOG_TITLE,
            self.wizard().choose_output_line_edit.text(),
            CHOOSE_OUTPUT_DIALOG_FILTER)[0]
        if not fn: return

        self.wizard().choose_output_line_edit.setText(fn)


    def isComplete(self) -> bool:
        """
        Return True if a reasonable save file path has been chosen;
        False otherwise
        """
        w = self.wizard()

        fn = w.choose_output_line_edit.text()

        if not fn.strip():
            w.choose_output_status_label.setText(CHOOSE_OUTPUT_STATUS_NONE)
            return False

        try:
            fn = Path(fn)
        except Exception:
            w.choose_output_status_label.setText(CHOOSE_OUTPUT_STATUS_INVALID)
            return False

        if fn.is_absolute():
            # We handle non-full paths by putting the rom in the same
            # folder as the input rom.

            if not fn.parent.is_dir():
                w.choose_output_status_label.setText(CHOOSE_OUTPUT_STATUS_INVALID)
                return False

            if fn.is_dir():  # Just in case?
                w.choose_output_status_label.setText(CHOOSE_OUTPUT_STATUS_INVALID)
                return False

            if fn.is_file():
                w.choose_output_status_label.setText(CHOOSE_OUTPUT_STATUS_EXISTS)
                return True  # This case is just a warning, not an error

            w.choose_output_status_label.setText('')
            return True

        else:
            if fn.is_file():
                w.choose_output_status_label.setText(CHOOSE_OUTPUT_STATUS_EXISTS)
                return True  # This case is just a warning, not an error

            w.choose_output_status_label.setText('')
            return True



class ConfirmationPage(QtWidgets.QWizardPage):
    """
    A wizard page that shows you all relevant info before the rom is
    actually patched
    """
    def __init__(self, wizard: QtWidgets.QWizard):
        super().__init__(wizard)
        self.setTitle(CONFIRMATION_HEADER)
        self.setSubTitle(CONFIRMATION_TEXT)
        self.setCommitPage(True)  # Disables the next page's Back button
                                  # and some other nice stuff

        # "Commit" sounds weird.
        self.setButtonText(wizard.CommitButton, CONFIRMATION_BUTTON_START)

        # Confirmation label
        label = QtWidgets.QLabel(self)
        label.setWordWrap(True)
        label.setText('')  # placeholder
        wizard.confirmation_label = label

        # Layout
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(label)


    def initializePage(self) -> None:
        """
        Prepare the page based on input from previous pages.
        """
        in_fp = self.wizard().choose_rom_line_edit.text()
        out_fp = self.wizard().choose_output_line_edit.text()

        new_text = CONFIRMATION_BODY
        new_text = new_text.replace('[in-path]', in_fp)
        new_text = new_text.replace('[out-path]', out_fp)

        self.wizard().confirmation_label.setText(new_text)



class FinishedPage(QtWidgets.QWizardPage):
    """
    A wizard page that tells you that, congratulations, Newer DS is
    ready to play
    """
    def __init__(self, wizard: QtWidgets.QWizard):
        super().__init__(wizard)

        # Finished label
        label = QtWidgets.QLabel(self)
        label.setWordWrap(True)
        label.setText('') # placeholder
        wizard.finished_label = label

        # Traceback box
        traceback_box = QtWidgets.QPlainTextEdit(self)
        traceback_box.setReadOnly(True)
        traceback_box.document().setDefaultFont(QtGui.QFont('monospace'))
        traceback_box.setPlainText('')
        wizard.finished_tracebackBox = traceback_box

        # Layout
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(label)
        L.addWidget(traceback_box)


    def initializePage(self) -> None:
        """
        Prepare the page based on input from previous pages.
        """

        # OK, now we can actually patch the thing.

        in_fp = Path(self.wizard().choose_rom_line_edit.text())
        out_fp = Path(self.wizard().choose_output_line_edit.text())

        success = True
        try:
            result = patch_rom(in_fp, out_fp)
        except Exception as e:
            success = False

            import traceback

            tb = traceback.format_exc()[:-1]  # strip trailing newline

            print(tb, file=sys.stderr)

        if success:
            header = FINISHED_HEADER_SUCCESS
            text = FINISHED_TEXT_SUCCESS
            traceback_text = ''

        else:
            header = FINISHED_HEADER_FAILURE
            text = FINISHED_TEXT_FAILURE
            traceback_text = tb

        self.setTitle(header)
        self.wizard().finished_label.setText(text)
        self.wizard().finished_tracebackBox.setPlainText(traceback_text)

        if success:
            self.wizard().finished_tracebackBox.hide()


def have_required_files() -> bool:
    """
    Check if all required files are present.
    """
    data_dir = Path('data')

    if not data_dir.is_dir():
        return False

    if not (data_dir / 'patches').is_dir():
        return False

    if len(list((data_dir / 'patches').iterdir())) != Info['patchesRequired']:
        return False

    data_files = [
        'info.json',
        'icon-16.png',
        'icon-24.png',
        'icon-32.png',
        'icon-48.png',
        'icon-64.png',
        'icon-128.png',
        'icon.ico',
        'logo.png',
        'watermark.png',
        'xdelta3.exe']

    if not all((data_dir / fn).is_file() for fn in data_files):
        return False

    return True


def main() -> None:
    global app
    app = QtWidgets.QApplication(sys.argv)

    data_dir = Path('data')

    # Check if info.json exists like it should (since we need to load it
    # in order to check that the rest of the files exist)
    if not (data_dir / 'info.json').is_file():
        QtWidgets.QMessageBox.warning(None, ERROR_MISSING_FILES_TITLE,  ERROR_MISSING_FILES_TEXT)

    # Now we can load the latest version info
    global Info
    with (data_dir / 'info.json').open('r', encoding='utf-8') as f:
        Info = json.load(f)

    # Now check that the rest of the required files are present
    if not have_required_files():
        QtWidgets.QMessageBox.warning(None, ERROR_MISSING_FILES_TITLE,  ERROR_MISSING_FILES_TEXT)
        return

    # We want to disable Qt.WindowContextHelpButtonHint on the wizard.
    # Calling setWindowFlags after creation doesn't work properly -- it
    # needs to be set in the constructor.
    # So we need to know what the default flags for a wizard are, and
    # then just disable that particular one.

    # This is kind of a hack, but it works fine
    default_flags = QtWidgets.QWizard(None).windowFlags()

    wizard = QtWidgets.QWizard(None, default_flags & ~Qt.WindowContextHelpButtonHint)

    wizard.addPage(create_welcome_page(wizard))
    wizard.addPage(ChooseRomPage(wizard))
    wizard.addPage(ChooseOutputPage(wizard))
    wizard.addPage(ConfirmationPage(wizard))
    wizard.addPage(FinishedPage(wizard))

    logo_pixmap = QtGui.QPixmap(str(data_dir / 'logo.png'))
    watermark_pixmap = QtGui.QPixmap(str(data_dir / 'watermark.png'))

    for id in wizard.pageIds():
        p = wizard.page(id)
        p.setPixmap(wizard.LogoPixmap, logo_pixmap)
        p.setPixmap(wizard.WatermarkPixmap, watermark_pixmap)
        p.setPixmap(wizard.BackgroundPixmap, watermark_pixmap)

    icon = QtGui.QIcon()
    for size in [16, 24, 32, 48, 64, 128]:
        icon.addPixmap(QtGui.QPixmap(str(data_dir / ('icon-%d.png' % size))))

    wizard.setWindowTitle(WINDOW_TITLE)
    wizard.setWindowIcon(icon)
    wizard.show()

    return app.exec_()


if __name__ == '__main__':
    main()
