from maya import cmds


# NOTE: ALL user data files will be placed in a master directory at the users scripts folder

def get_user_scripts_folder():
    """get the maya users local scripts folder
    :return str: users maya scripts path. example C:/Users/UserName/Documents/maya/scripts/"""
    user_scripts_directory = cmds.internalVar(usd=True)
    mayas_scripts = '{0}/{1}'.format(user_scripts_directory.rsplit('/', 3)[0], 'scripts/')
    return mayas_scripts

USER_DATA_PATH = "{0}as_maya_tools_user_data".format(get_user_scripts_folder())

REPO_DATA_PATH = "{0}as_maya_tools".format(get_user_scripts_folder())

RIG_DEFINITION_CONTEXT_PATH = "{0}/RIG_DEFINITION_CONTEXTS".format(USER_DATA_PATH)

RIG_SELECTION_SETTINGS_PATH = "{0}/RIG_SELECTION_SETTINGS".format(USER_DATA_PATH)

NOISE_GENERATION_SETTINGS_PATH = "{0}/NOISE_GENERATION_SETTINGS_PATH".format(USER_DATA_PATH)

STYLE_SHEETS_PATH = "{0}/stylesheets".format(REPO_DATA_PATH)