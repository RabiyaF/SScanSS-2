import logging
import os
from enum import Enum, unique
from .model import MainWindowModel


@unique
class MessageReplyType(Enum):
    Save = 1
    Discard = 2
    Cancel = 3

class MainWindowPresenter:
    def __init__(self, view):
        self.view = view
        self.model = MainWindowModel()

    def isProjectCreated(self):
        return True if self.model.project_data else False

    def createProject(self, name, instrument):
            self.model.createProjectData(name, instrument)
            self.view.showProjectName(name)

    def saveProject(self, save_as=False):
        if not self.isProjectCreated():
            return

        # Avoids saving when there are no changes
        if not self.model.unsaved and self.model.save_path and not save_as:
            return

        filename = self.model.save_path
        if save_as or not filename:
            filename = self.view.showSaveDialog('hdf5 File (*.h5)',
                                                current_dir=filename)
        if not filename:
            return

        try:
            self.model.saveProjectData(filename)
        except OSError:
            msg = 'A error occurred while attempting to save this project ({})'.format(filename)
            logging.error(msg)
            self.view.showErrorMessage(msg)

    def openProject(self):
        if not self.confirmSave():
            return

        filename = self.view.showOpenDialog('hdf5 File (*.h5)',
                                            current_dir=self.model.save_path)
        if not filename:
            return

        try:
            self.model.loadProjectData(filename)
            self.view.showProjectName(self.model.project_data['name'])
        except (KeyError, AttributeError):
            msg = '{} could not open because it has an incorrect format.'
            msg = msg.format(os.path.basename(filename))
            logging.error(msg)
            self.view.showErrorMessage(msg)

    def confirmSave(self):
        """
        Checks if the project is saved and asks the user to save if necessary

        :return: True if the project is saved or user chose to discard changes
        :rtype: bool
        """
        if not self.model.unsaved:
            return True

        reply = self.view.showSaveDiscardMessage(self.model.project_data['name'])

        if reply == MessageReplyType.Save:
            if self.model.save_path:
                self.saveProject()
                return True
            else:
                self.saveProject(save_as=True)
                return False if self.model.unsaved else True

        elif reply == MessageReplyType.Discard:
            return True

        else:
            return False
