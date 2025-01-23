from maya import cmds


# NOTE: ALL user data files will be placed in a master directory at the users scripts folder

def get_user_scripts_folder():
    """get the maya users local scripts folder
    :return str: users maya scripts path. example C:/Users/UserName/Documents/maya/scripts/"""
    user_scripts_directory = cmds.internalVar(usd=True)
    mayas_scripts = '{0}/{1}'.format(user_scripts_directory.rsplit('/', 3)[0], 'scripts/')
    return mayas_scripts

USER_DATA_PATH = "{0}as_maya_tools_user_data".format(get_user_scripts_folder())