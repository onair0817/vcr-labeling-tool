import glob
import re
import json
import os
import sys
import codecs
import shutil
import cv2

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .name_dialog import NameDialog
from .point import Point
from .image_widget import ImageWidget

import main_window_ui

# TARGET_CONTENT = 'KOBACO'
TARGET_CONTENT = 'NIA'


class MainWindow(QMainWindow, main_window_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi(os.path.abspath("main_window.ui"), self)
        self.setupUi(self)

        self.json_files = []  # List of absolute paths to all json files
        self.json_file_idx = None  # Current selected json file index
        self.img_file = ''  # Current selected image file absolute path
        self.img_json = {}  # Current selected image JSON data

        self.img_height = 0  # Current selected image height
        self.img_width = 0  # Current selected image width
        self.img_bboxes = []  # Current selected image bboxes
        self.img_names = []  # Current selected image bbox names
        self.img_names_scores = []
        self.img_bbox_idx = None  # Current selected image - selected box

        self.content_type = "object"

        self.names_dir = os.path.abspath("names")
        self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-object-hangul.names")
        self.name_list = []

        self.color_change = []
        self.init_widgets()

    def init_widgets(self):
        """Initialize image widget and connections."""
        self.imgWidget = ImageWidget(self, objectName="img")
        self.mainLayout.insertWidget(0, self.imgWidget)

        # Make list items non-editable
        self.fileList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.idList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Initial settings
        self.objectRadioButton.setChecked(True)
        self.radio_button_action("object")

        # Connections
        self.loadAction.triggered.connect(self.load_action)
        self.saveAction.triggered.connect(self.save_action)
        self.deleteAction.triggered.connect(self.delete_action)
        self.newBoxAction.triggered.connect(self.new_box_action)
        self.entireImageAction.triggered.connect(self.entire_image_action)
        self.prevPageButton.clicked.connect(self.prev_button_action)
        self.nextPageButton.clicked.connect(self.next_button_action)
        self.objectRadioButton.clicked.connect(lambda: self.radio_button_action("object"))
        self.faceRadioButton.clicked.connect(lambda: self.radio_button_action("face"))
        # self.ageGenderRadioButton.clicked.connect(lambda: self.radio_button_action("age-gender"))
        # self.brandRadioButton.clicked.connect(lambda: self.radio_button_action("brand"))
        self.sceneRadioButton.clicked.connect(lambda: self.radio_button_action("scene"))
        # self.landmarkRadioButton.clicked.connect(lambda: self.radio_button_action("landmark"))
        self.nameDialogButton.clicked.connect(self.name_dialog_button_action)
        self.currentPageEdit.returnPressed.connect(self.current_page_action)
        self.fileList.selectionChanged = self.file_selection_changed
        self.idList.selectionChanged = self.name_selection_changed

    def load_action(self):
        """Open file dialog and get directory of json files."""
        dir_name = QFileDialog.getExistingDirectory(self)
        self.json_files = self.get_filenames(dir_name,
                                             extensions=['json'],
                                             recursive_=True, exit_=False)
        # self.json_files = glob.glob(f"{dir_name}/*.json")
        # self.img_files.extend(glob.glob(f"{dir_name}/*.png"))

        def key(string):
            key_list = []
            for c in re.split('([0-9]+)', string):
                if string.isdigit():
                    key_list.append(int(string))
                else:
                    key_list.append(string.lower())

            return key_list

        self.json_files = sorted(self.json_files, key=key)
        self.json_file_idx = 0

        self.process_image()
        self.update_file_list_ui()
        self.update_ui()

    def process_image(self):
        """Load json data for current file."""
        if not self.json_files:
            return

        dir_name = os.path.dirname(self.json_files[self.json_file_idx])
        file_root = os.path.splitext(os.path.basename(self.json_files[self.json_file_idx]))[0]
        img_dir_name = dir_name.replace('Image.json', 'Image.ext')
        self.img_file = os.path.join(img_dir_name, f"{file_root.replace('VCR.', '')}.jpg")

        if not os.path.exists(self.json_files[self.json_file_idx]):
            cv2_img = cv2.imread(self.img_file)
            cv2_img_width = cv2_img.shape[1]
            cv2_img_height = cv2_img.shape[0]

            # img_size = os.path.getsize(self.img_files[self.img_file_idx])

            self.img_json = {
                "dataset": {
                    "description": "",
                    "version": "1.0",
                    "date_created": "",
                    "attributes": {
                        "augmented": False,
                        "answer_refined": True
                    }
                },
                "image": {
                    "file_name": file_root,
                    "attributes": {
                        "color": 3,
                        "width": cv2_img_width,
                        "height": cv2_img_height,
                        "url": self.img_file
                    }
                },
                "content": {
                    "face": {
                        "algorithm": {
                            "detect_algorithm": None,
                            "recog_algorithm": "",
                            "age_gender_algorithm": None,
                            "detect_model": None,
                            "recog_model": "",
                            "age_gender_model": None
                        },
                        "annotation": {
                            "bboxes": [],
                            "vectors": [],
                            "ids": None,
                            "names": [],
                            "scores": [],
                            "ages": None,
                            "genders": None
                        }
                    },
                    "object": {
                        "algorithm": {
                            "algorithm": "",
                            "model": "",
                            "name_list": None
                        },
                        "annotation": {
                            "bboxes": [],
                            "ids": None,
                            "names": [],
                            "scores": []
                        }
                    },
                    "brand": {
                        "algorithm": {
                            "algorithm": None,
                            "model": None,
                            "name_list": None
                        },
                        "annotation": {
                            "bboxes": None,
                            "ids": None,
                            "names": None,
                            "scores": None
                        }
                    },
                    "scene": {
                        "algorithm": {
                            "algorithm": "",
                            "model": "",
                            "name_list": ""
                        },
                        "annotation": {
                            "ids": [],
                            "names": [],
                            "scores": []
                        }
                    },
                    "landmark": {
                        "algorithm": {
                            "algorithm": None,
                            "model": None,
                            "name_list": None
                        },
                        "annotation": {
                            "bboxes": None,
                            "names": None,
                            "ids": None,
                            "scores": None
                        }
                    },
                    "text": {
                        "algorithm": {
                            "algorithm": None,
                            "model": None
                        },
                        "annotation": {
                            "classes": None,
                            "languages": None,
                            "bboxes": None,
                            "texts": None,
                            "legibilities": None,
                            "scores": None
                        }
                    }
                }
            }

            with open(self.json_files[self.json_file_idx], 'w', encoding='utf-8') as json_file:
                json.dump(self.img_json, json_file, ensure_ascii=False, indent=4)

        else:
            self.img_json = json.load(codecs.open(self.json_files[self.json_file_idx], 'r', 'utf-8-sig'))

        if self.content_type:
            if self.img_json['content'][self.content_type]['annotation']['bboxes']:
                self.img_names = self.img_json['content'][self.content_type]['annotation']['names']
                self.img_names_scores = self.img_json['content'][self.content_type]['annotation']['scores']
                self.img_width = self.img_json['image']['attributes']['width']
                self.img_height = self.img_json['image']['attributes']['height']
            else:
                self.img_json['content'][self.content_type]['annotation']['bboxes'] = []
                self.img_names = []
                self.img_names_scores = []
                self.img_width = self.img_json['image']['attributes']['width']
                self.img_height = self.img_json['image']['attributes']['height']

            # bbox가 있는 경우
            if 'bboxes' in self.img_json['content'][self.content_type]['annotation']:
                # TODO 약간 inference 결과가 이상해 임시방편으로 해결해둔 것
                # Turn JSON list into list of Points
                self.img_bboxes = list(map(lambda a: [
                    Point(self.img_width * a[0], self.img_height * a[1]),
                    Point(self.img_width * a[2], self.img_height * a[1]),
                    Point(self.img_width * a[2], self.img_height * a[3]),
                    Point(self.img_width * a[0], self.img_height * a[3])
                ], self.img_json['content'][self.content_type]['annotation']['bboxes']))

                self.color_change = len(self.img_bboxes) * [False]

                self.img_bbox_idx = 0
                self.update_name_list_ui()
            # Scene 과 같이 bbox 가 없을 때의 처리 방법
            elif self.content_type == 'scene':
                self.img_bboxes = []
                self.img_bbox_idx = 0
                self.update_file_list_ui()

    def update_ui(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        self.statusLabel.clear()

        # Update image
        pix_map_image = QPixmap(self.img_file)

        self.imgWidget.setPixmap(pix_map_image)
        self.imgWidget.setScaledContents(True)

        # Update page selection
        self.currentPageEdit.setText(str(self.json_file_idx + 1))
        self.currentPageEdit.setValidator(
            QIntValidator(1, len(self.json_files), self))
        self.totalPageLabel.setText(f"/ {len(self.json_files)}")

        # Update list selections
        self.fileList.setCurrentIndex(
            self.fileList.model().createIndex(self.json_file_idx if self.json_file_idx else 0, 0))

        self.idList.setCurrentIndex(
            self.idList.model().createIndex(self.img_bbox_idx if self.img_bbox_idx else 0, 0))

    def update_file_list_ui(self):
        """Update model for file list."""
        model = QStandardItemModel()
        for json_file in self.json_files:
            model.appendRow(QStandardItem(os.path.basename(json_file)))

        self.fileList.setModel(model)

    def update_name_list_ui(self):
        """Update model for text list."""
        model = QStandardItemModel()
        for name in self.img_names:
            model.appendRow(QStandardItem(str(name)))

        self.idList.setModel(model)

    def prev_button_action(self):
        """Go to previous image, do nothing if already at beginning."""
        if self.json_file_idx > 0:
            self.save_action()
            self.json_file_idx -= 1
            self.process_image()
            self.update_ui()

    def next_button_action(self):
        """Go to next image, do nothing if already at end."""
        if self.json_file_idx < len(self.json_files) - 1:
            self.save_action()
            self.json_file_idx += 1
            self.process_image()
            self.update_ui()

    def current_page_action(self):
        """Go to specific image entered into page selection."""
        if int(self.currentPageEdit.text()) - 1 != self.json_file_idx:
            self.json_file_idx = int(self.currentPageEdit.text()) - 1
            self.process_image()
            self.update_ui()

    def radio_button_action(self, content_type):
        self.content_type = str(content_type)

        if content_type == "object":
            self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-object-hangul.names")
            self.newBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
        elif content_type == "face":
            self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-face-hangul.names")
            self.newBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
        elif content_type == "brand":
            self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-brand-hangul.names")
            self.newBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
        elif content_type == "scene":
            self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-scene-hangul.names")
            self.newBoxAction.setEnabled(False)
            self.entireImageAction.setEnabled(False)
        elif content_type == "landmark":
            self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-landmark-hangul.names")
            self.newBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
        else:
            self.names_file = os.path.join(self.names_dir, "idle.names")
            self.newBoxAction.setEnabled(False)
            self.entireImageAction.setEnabled(False)

        # Not in list
        self.name_list = []

        with open(self.names_file, 'r', encoding='utf-8') as c:
            names_strings = c.read()
        for one_line in names_strings.split('\n'):
            splits = one_line.split(',')
            if len(splits) == 2:
                self.name_list.append(str(splits[1].strip()))
            else:
                self.name_list.append(str(splits[-1].strip()))

        print(" # Content type is {} ({})".format(self.content_type, self.names_file))

        self.process_image()
        self.update_ui()

    def name_dialog_button_action(self):
        try:
            dialog = NameDialog(self)
            dialog.exec_()
        except (TypeError, IndexError):
            self.statusLabel.setText("No Box available")

    def save_action(self):
        """Save data back to json file."""
        try:
            # check if the input can be converted to int
            self.update_name_list_ui()

            self.img_json['dataset']['attributes']['answer_refined'] = True

            self.img_json['content'][self.content_type]['annotation']['names'] = self.img_names
            self.img_json['content'][self.content_type]['annotation']['scores'] = self.img_names_scores

            # Turn list of Points back into JSON list
            self.img_json['content'][self.content_type]['annotation']['bboxes'] = []
            for idx1, bbox in enumerate(self.img_bboxes):
                self.img_json['content'][self.content_type]['annotation']['bboxes'].append([0, 0, 0, 0])
                for idx2, p in enumerate(bbox):
                    if idx2 == 0:
                        self.img_json['content'][self.content_type]['annotation']['bboxes'][idx1][0] = \
                            p.x / self.img_width
                        self.img_json['content'][self.content_type]['annotation']['bboxes'][idx1][1] = \
                            p.y / self.img_height
                    if idx2 == 2:
                        self.img_json['content'][self.content_type]['annotation']['bboxes'][idx1][2] = \
                            p.x / self.img_width
                        self.img_json['content'][self.content_type]['annotation']['bboxes'][idx1][3] = \
                            p.y / self.img_height

            original_file = f"{self.json_files[self.json_file_idx]}~"
            shutil.copy2(self.json_files[self.json_file_idx], original_file)

            with open(self.json_files[self.json_file_idx], 'w', encoding='utf-8') as json_file:
                json.dump(self.img_json, json_file, ensure_ascii=False, indent=4)

            self.statusLabel.setText("Saved!")
        except IndexError:
            self.statusLabel.setText("Invalid Text")

    def delete_action(self):
        if len(self.img_bboxes) > 0:
            """Delete current selected bbox."""
            del self.img_bboxes[self.img_bbox_idx]
            del self.img_names[self.img_bbox_idx]
            del self.img_names_scores[self.img_bbox_idx]

            if self.img_bbox_idx == len(self.img_bboxes):
                self.img_bbox_idx -= 1

        self.update_name_list_ui()
        self.update_ui()

    def new_box_action(self):
        """Add a new box with default size and text."""
        self.img_bboxes.append([Point(0, 0), Point(100, 0), Point(100, 100), Point(0, 100)])
        self.img_names.append("--추가해주세요--")
        self.img_names_scores.append(1.0)

        self.update_name_list_ui()
        self.update_ui()

    def entire_image_action(self):
        """Change current bbox to cover entire image."""
        try:
            self.img_bboxes[self.img_bbox_idx] = [
                Point(0, 0),
                Point(self.img_width, 0),
                Point(self.img_width, self.img_height),
                Point(0, self.img_height)
            ]
            self.update_ui()
        except IndexError:
            self.statusLabel.setText("Box unavailable")

    def file_selection_changed(self, selected, _):
        """Get new file selection and update UI."""
        indexes = selected.indexes()
        if len(indexes) <= 0:
            return

        self.save_action()
        self.json_file_idx = indexes[0].row()

        self.process_image()
        self.update_ui()

    def name_selection_changed(self, selected, _):
        """Get new id selection and update UI."""
        indexes = selected.indexes()
        if len(indexes) <= 0:
            return
        self.img_bbox_idx = indexes[0].row()
        if self.img_bboxes:
            self.color_change = len(self.img_bboxes) * [0]

            for i, name in enumerate(self.img_names):
                if name not in self.name_list:
                    self.color_change[i] = 2

            self.color_change[self.img_bbox_idx] = 1

        self.update_ui()

    @staticmethod
    def get_filenames(dir_path, prefixes=('',), extensions=('',), recursive_=True, exit_=False):
        """
        Find all the files starting with prefixes or ending with extensions in the directory path.
        ${dir_path} argument can accept file.

        :param dir_path:
        :param prefixes:
        :param extensions:
        :param recursive_:
        :param exit_:
        :return:
        """
        if os.path.isfile(dir_path):
            if os.path.splitext(dir_path)[1][1:] in extensions:
                return [dir_path]
            else:
                return []

        filenames = glob.glob(dir_path + '/**', recursive=recursive_)
        for i in range(len(filenames) - 1, -1, -1):
            basename = os.path.basename(filenames[i])
            if not (os.path.isfile(filenames[i]) and
                    basename.startswith(tuple(prefixes)) and
                    basename.endswith(tuple(extensions))):
                del filenames[i]

        if len(filenames) == 0:
            print(" @ Error: no file detected in {}".format(dir_path))
            if exit_:
                sys.exit(1)

        return filenames
