import os

from maya import cmds


# NOTE: ALL user data files will be placed in a master directory at the users scripts folder

def get_user_scripts_folder():
    """get the maya users local scripts folder
    :return str: users maya scripts path. example C:/Users/UserName/Documents/maya/scripts/"""
    user_scripts_directory = cmds.internalVar(usd=True)
    mayas_scripts = '{0}/{1}'.format(user_scripts_directory.rsplit('/', 3)[0], 'scripts/')
    return mayas_scripts


USER_DATA_PATH = f"{get_user_scripts_folder()}as_maya_tools_user_data"

REPO_DATA_PATH = os.path.dirname(os.path.abspath(__file__))

ICONS = f"{REPO_DATA_PATH}/icons"

RIG_DEFINITION_CONTEXT_PATH = f"{USER_DATA_PATH}/RIG_DEFINITION_CONTEXTS"

RIG_SELECTION_SETTINGS_PATH = f"{USER_DATA_PATH}/RIG_SELECTION_SETTINGS"

SELECTION_SET_DIRECTORY = f"{USER_DATA_PATH}/SELECTION_SETS"

SELECTION_SET_MANAGER_SETTINGS_PATH = f"{USER_DATA_PATH}/SELECTION_SET_MANAGER_SETTINGS"

SNAP_SETTINGS_PATH = f"{USER_DATA_PATH}/SNAP_SETTINGS"

NOISE_GENERATION_SETTINGS_PATH = f"{USER_DATA_PATH}/NOISE_GENERATION_SETTINGS_PATH"

SPACE_SWITCHER_SETTINGS_PATH = f"{USER_DATA_PATH}/SPACE_SWITCHER_SETTINGS_PATH"

STYLE_SHEETS_PATH = f"{REPO_DATA_PATH}/stylesheets"

KEYFRAME_DATA_PATH = f"{USER_DATA_PATH}/KEYFRAME_DATA_PATH"

COPY_PASTE_KEYFRAME_SETTINGS_PATH = f"{USER_DATA_PATH}/COPY_PASTE_KEYFRAME_SETTINGS_PATH"
