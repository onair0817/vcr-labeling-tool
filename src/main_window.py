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

IMG_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tif', 'tiff']
TARGET_CONTENT = 'KOBACO'
# TARGET_CONTENT = 'NIA'

OBJECT_LIST = ['사람', '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트', '신호등', '소화전', '정지 신호', '주차 미터기', '벤치', '새', '고양이', '개', '말', '양', '소', '코끼리', '곰', '얼룩말', '기린', '배낭', '우산', '핸드백', '넥타이', '여행 가방', '프리스비', '스키', '스노보드', '스포츠 공', '연', '야구 방망이', '야구 글러브', '스케이트보드', '서핑보드', '테니스 라켓', '유리병', '와인잔', '컵', '포크', '나이프', '숟가락', '그릇', '바나나', '사과', '샌드위치', '오렌지', '브로콜리', '당근', '핫도그', '피자', '도넛', '케이크', '의자', '소파', '화분에 심은 식물', '침대', '식탁', '변기', '텔레비전', '노트북', '마우스', '리모트컨트롤', '키보드', '핸드폰', '전자레인지', '오븐', '토스터', '싱크대', '냉장고', '책', '시계', '꽃병', '가위', '곰인형', '헤어드라이어', '칫솔', '베너', '담요', '나무가지', '다리', '건물', '관목', '케비넷', '케이지', '판지', '카펫', '천장', '천장타일', '옷감', '옷', '구름', '카운터', '찬장', '커튼', '탁상용의 물건', '흙', '문짝', '울타리', '마블마루', '바닥', '돌마루', '타일마루', '나무마루', '꽃', '안개', '음식', '과일', '가구', '풀', '자갈', '운동장', '언덕', '집', '나뭇잎', '불빛', '매트', '금속', '거울', '이끼', '산', '진흙', '냅킨', '그물', '종이', '포장 도로', '베개', '식물', '플라스틱', '플랫폼', '운동장', '난간', '철길', '강', '도로', '바위', '지붕', '깔개', '샐러드', '모래', '바다', '선반', '하늘', '마천루', '눈', '고체', '층계단', '돌', '짚단', '구조물', '테이블', '텐트', '직물', '수건', '나무', '채소', '벽돌 벽', '콘크리트 벽', '벽', '패널 벽', '돌 벽', '타일 벽', '목재 벽', '물', '물방울', '창문가리개', '창', '목재', '기타']
FACE_LIST = ['강다니엘', '강동원', '강석우', '강소라', '강하늘', '강호동', '고수', '고아라', '고윤정', '공유', '공효진', '권나라', '김강훈', '김고은', '김구라', '김남주', '김다미', '김동완', '김동현(격투기선수)', '김래원', '김명민', '김미숙', '김민아(1991)', '김병만', '김병철', '김보라(1995)', '김보성', '김사랑', '김상중', '김서형', '김성령', '김성주', '김세정(구구단)', '김소연', '김수미', '김수현', '김숙', '김승우', '김연경(배구선수)', '김연아', '김영옥', '김영철(배우)', '김유정(배우)', '김정현(1990)', '김종국', '김준현(개그맨)', '김지원', '김지호', '김태리', '김태희', '김하늘', '김해숙', '김향기', '김혜수', '김혜윤', '김혜자', '김희선', '김희애', '김희철', '나나(애프터스쿨)', '나연(트와이스)', '남궁민', '남승민(가수)', '남주혁', '다니엘헤니', '도경수(EXO)', '라미란', '류준열', '마동석', '문근영', '문세윤', '문채원', '박건후(2017)', '박나래', '박나은(2015)', '박미선', '박민영', '박보검', '박보영', '박서준', '박소담', '박신혜', '박은빈', '박인비', '박지훈(워너원)', '박해수', '박해진', '배정남', '백종원', '백현(EXO)', '뷔(BTS)', '비(정지훈)', '비와이', '사나(트와이스)', '사이먼도미닉', '샘해밍턴', '서은수', '서장훈', '서지혜', '서현(소녀시대)', '서현진', '선미(원더걸스)', '설리(에프엑스)', '설인아', '설현', '성유리', '성훈(방성훈)', '소유', '소유진', '소이현', '소지섭', '손나은', '손담비', '손연재(체조선수)', '손예진', '손흥민', '솔라(마마무)', '송가인', '송민호', '송소희', '송승헌', '송중기', '송지효', '송혜교', '수지', '슈가(BTS)', '슬기(레드벨벳)', '신구', '신동엽', '신민아', '신세경', '신혜선', '심형탁', '아이린(레드벨벳)', '안보현', '안성기', '안정환', '안현모', '양세형', '양희은', '에릭남', '여진구', '염정아', '영탁', '오정세', '오혜원', '옹성우', '요요미', '원빈', '윌리엄해밍턴', '유동근', '유라(걸스데이)', '유병재', '유승호', '유아인', '유연석', '유이(애프터스쿨)', '유인나', '유재석', '유지태', '유해진', '윤보미(에이핑크)', '윤아(소녀시대)', '이경규', '이나영', '이다희', '이덕화', '이동욱', '이민정', '이민호', '이병헌', '이보영', '이상우', '이상윤', '이서진', '이선균', '이성경', '이성민', '이세영(배우)', '이솜', '이수근', '이순재', '이승기', '이시언', '이연복', '이연희', '이영애', '이영자', '이정은(1970)', '이정재', '이제훈', '이종석', '이준기', '이지은(아이유)', '이하늬', '이효리', '임시완', '임영웅', '임원희', '장나라', '장도연', '장동건', '장성규', '장윤정', '장윤주', '장혁', '전미도', '전소미', '전소민', '전여빈', '전인화', '전지현', '전현무', '정국(BTS)', '정상훈', '정우성', '정유미(1983)', '정유미(1984)', '정윤호(유노윤호)', '정인선', '정준호', '정채연(다이아)', '정해인', '제니(블랙핑크)', '조보아', '조세호', '조승우', '조여정', '조우진', '조인성', '조정석', '조진웅', '주이(모모랜드)', '주지훈', '지민(BTS)', '지성', '지진희', '지효(트와이스)', '진(BTS)', '차승원', '차은우', '차인표', '차태현', '천우희', '청하', '첸(EXO)', '최불암', '최수종', '최우식', '추대엽(카피추)', '크리스탈(에프엑스)', '태연(소녀시대)', '피오(블락비)', '하니(EXID)', '하석진', '하정우', '하지원', '한가인', '한고은', '한석규', '한소희', '한예슬', '한지민', '한채영', '한현민', '한혜진(모델)', '한혜진(배우)', '한효주', '헨리', '현빈', '혜리(걸스데이)', '호시(세븐틴)', '홍은희', '홍종현', '홍진경', '홍진영', '화사(마마무)', '황광희', '황정민', '황제성']
BRAND_LIST = ['에이스침대', '애플', '코카콜라', '동국제약', '동서식품', '다이슨', '페브리즈', '현대', 'ibk기업은행', '정관장', 'KT', '광동제약', 'LG', '라이프플러스', '롯데', '맥도날드', '명인제약', '삼성', '서울우유', 'SK텔레콤']
SCENE_LIST = ['비행장', '비행기선실']
LANDMARK_LIST = ['4.19학생혁명기념탑', '43기념관', '518민주묘지상징탑', '63빌딩', '83타워', 'DGB대구은행파크', 'G 챔피언스 파크']
IDLE_LIST = []

class MainWindow(QMainWindow, main_window_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi(os.path.abspath("main_window.ui"), self)
        self.setupUi(self)

        self.ext_dir = ''
        self.json_dir = ''
        self.json_files = []  # List of absolute paths to all json files
        self.json_file_idx = None  # Current selected json file index
        self.img_file = ''  # Current selected image file absolute path
        self.img_json = {}  # Current selected image JSON data

        self.img_height = 0  # Current selected image height
        self.img_width = 0  # Current selected image width
        self.img_bboxes = []  # Current selected image bboxes
        self.img_ids = []  # Current selected image ids
        self.img_names = []  # Current selected image bbox names
        self.img_names_scores = []  # Current selected image bbox names' scores
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
        self.nameList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Initial settings
        self.objectRadioButton.setChecked(True)
        self.radio_button_action("object")

        # Connections
        self.loadAction.triggered.connect(self.load_action)
        self.saveAction.triggered.connect(self.save_action)
        self.nameDialogAction.triggered.connect(self.name_dialog_button_action)
        self.newSceneAction.triggered.connect(self.new_scene_action)
        self.newBoxAction.triggered.connect(self.new_box_action)
        self.deleteBoxAction.triggered.connect(self.delete_box_action)
        self.deleteSceneAction.triggered.connect(self.delete_scene_action)
        self.entireImageAction.triggered.connect(self.entire_image_action)
        self.prevPageButton.clicked.connect(self.prev_button_action)
        self.nextPageButton.clicked.connect(self.next_button_action)
        self.objectRadioButton.clicked.connect(lambda: self.radio_button_action("object"))
        self.faceRadioButton.clicked.connect(lambda: self.radio_button_action("face"))
        # self.ageGenderRadioButton.clicked.connect(lambda: self.radio_button_action("age-gender"))
        self.brandRadioButton.clicked.connect(lambda: self.radio_button_action("brand"))
        self.sceneRadioButton.clicked.connect(lambda: self.radio_button_action("scene"))
        self.landmarkRadioButton.clicked.connect(lambda: self.radio_button_action("landmark"))
        self.nameDialogButton.clicked.connect(self.name_dialog_button_action)
        self.currentPageEdit.returnPressed.connect(self.current_page_action)
        self.fileList.selectionChanged = self.file_selection_changed
        self.nameList.selectionChanged = self.name_selection_changed

    def load_action(self):
        def key(string):
            key_list = []
            for c in re.split('([0-9]+)', string):
                if string.isdigit():
                    key_list.append(int(string))
                else:
                    key_list.append(string.lower())

            return key_list

        """Open file dialog and get directory of json files."""
        json_dir = QFileDialog.getExistingDirectory(self)
        self.json_dir = json_dir
        self.ext_dir = os.path.join(json_dir.split('Image.json')[0], 'Image.ext')
        self.json_files = self.get_filenames(json_dir,
                                             extensions=['json'],
                                             recursive_=True, exit_=False)

        self.json_files = sorted(self.json_files, key=key)
        self.json_file_idx = 0

        self.process_image()
        self.update_file_list_ui()
        self.update_ui()

    def process_image(self):
        def key(string):
            key_list = []
            for c in re.split('([0-9]+)', string):
                if string.isdigit():
                    key_list.append(int(string))
                else:
                    key_list.append(string.lower())

            return key_list

        """Load json data for current file."""
        if not self.json_files:
            return

        json_cat_folder_name = self.json_dir.split("/")[-1]
        json_dir = os.path.dirname(self.json_files[self.json_file_idx])
        json_vid_folder_name = json_dir.split("/")[-1]
        json_file_name = os.path.basename(self.json_files[self.json_file_idx])


        img_cat_folder_name = json_cat_folder_name.split("_")[0]
        img_dir = os.path.join(self.ext_dir, img_cat_folder_name, json_vid_folder_name)

        img_files = self.get_filenames(img_dir,
                                       extensions=IMG_EXTENSIONS,
                                       recursive_=True, exit_=False)

        img_files = sorted(img_files, key=key)

        for img_file in img_files:
            if str(os.path.splitext(img_file)[-1]).replace(".", "") in IMG_EXTENSIONS:
                if os.path.splitext(str(json_file_name.replace("VCR.", "")))[0] == os.path.splitext(os.path.basename(img_file))[0]:
                    self.img_file = img_file
                    break

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
                    "file_name": os.path.splitext(str(json_file_name))[0],
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
            # bbox가 있는 경우
            if 'bboxes' in self.img_json['content'][self.content_type]['annotation']:
                if self.img_json['content'][self.content_type]['annotation']['bboxes']:
                    self.img_ids = self.img_json['content'][self.content_type]['annotation']['ids']
                    self.img_names = self.img_json['content'][self.content_type]['annotation']['names']
                    self.img_names_scores = self.img_json['content'][self.content_type]['annotation']['scores']
                    self.img_width = self.img_json['image']['attributes']['width']
                    self.img_height = self.img_json['image']['attributes']['height']
                else:
                    self.img_json['content'][self.content_type]['annotation']['bboxes'] = []
                    self.img_ids = []
                    self.img_names = []
                    self.img_names_scores = []
                    self.img_width = self.img_json['image']['attributes']['width']
                    self.img_height = self.img_json['image']['attributes']['height']

                # Turn JSON list into list of Points
                self.img_bboxes = list(map(lambda a: [
                    Point(self.img_width * a[0], self.img_height * a[1]),
                    Point(self.img_width * a[2], self.img_height * a[1]),
                    Point(self.img_width * a[2], self.img_height * a[3]),
                    Point(self.img_width * a[0], self.img_height * a[3])
                ], self.img_json['content'][self.content_type]['annotation']['bboxes']))

                self.color_change = len(self.img_bboxes) * [False]

                self.img_bbox_idx = 0

                idx_to_be_removed = []
                for idx in range(len(self.img_names)):
                    if self.content_type == 'face' and self.img_names[idx].lower() == 'nobody':
                        idx_to_be_removed.append(idx)

                # Remove 'nobody' face
                if self.img_ids:
                    self.img_bboxes = [i for j, i in enumerate(self.img_bboxes) if j not in idx_to_be_removed]
                    self.img_ids = [i for j, i in enumerate(self.img_ids) if j not in idx_to_be_removed]
                    self.img_names = [i for j, i in enumerate(self.img_names) if j not in idx_to_be_removed]
                    self.img_names_scores = [i for j, i in enumerate(self.img_names_scores) if j not in idx_to_be_removed]

                self.update_name_list_ui()

            # Scene 과 같이 bbox 가 없을 때의 처리 방법
            elif self.content_type == 'scene' or self.content_type == 'landmark':
                self.img_ids = self.img_json['content'][self.content_type]['annotation']['ids']
                self.img_names = self.img_json['content'][self.content_type]['annotation']['names']
                self.img_names_scores = self.img_json['content'][self.content_type]['annotation']['scores']
                self.img_width = self.img_json['image']['attributes']['width']
                self.img_height = self.img_json['image']['attributes']['height']
                self.img_bboxes = []
                self.img_bbox_idx = 0

                if not self.img_ids:
                    self.img_ids = []
                if not self.img_names:
                    self.img_names = []
                if not self.img_names_scores:
                    self.img_names_scores = []

                idx_to_be_removed = []
                for idx in range(len(self.img_names)):
                    if self.content_type == 'landmark':
                        idx_to_be_removed.append(idx)
                    elif self.img_names_scores[idx] < 0.7:
                        idx_to_be_removed.append(idx)

                self.img_ids = [i for j, i in enumerate(self.img_ids) if j not in idx_to_be_removed]
                self.img_names = [i for j, i in enumerate(self.img_names) if j not in idx_to_be_removed]
                self.img_names_scores = [i for j, i in enumerate(self.img_names_scores) if j not in idx_to_be_removed]

                self.update_name_list_ui()

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

        self.nameList.setCurrentIndex(
            self.nameList.model().createIndex(self.img_bbox_idx if self.img_bbox_idx else 0, 0))

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

        self.nameList.setModel(model)

    def prev_button_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        """Go to previous image, do nothing if already at beginning."""
        if self.json_file_idx > 0:
            self.save_action()
            self.json_file_idx -= 1
            self.process_image()
            self.update_ui()

    def next_button_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

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

    # @@@ Put names info into main_window.py because of packaging
    def radio_button_action(self, content_type):
        self.save_action()
        self.content_type = str(content_type)

        if content_type == "object":
            # self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-object-hangul.names")
            self.names_file = "OBJECT"
            self.name_list = OBJECT_LIST
            self.newBoxAction.setEnabled(True)
            self.deleteBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
            self.newSceneAction.setEnabled(False)
            self.deleteSceneAction.setEnabled(False)
        elif content_type == "face":
            # self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-face-hangul.names")
            self.names_file = "FACE"
            self.name_list = FACE_LIST
            self.newBoxAction.setEnabled(True)
            self.deleteBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
            self.newSceneAction.setEnabled(False)
            self.deleteSceneAction.setEnabled(False)
        elif content_type == "brand":
            # self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-brand-hangul.names")
            self.names_file = "BRAND"
            self.name_list = BRAND_LIST
            self.newBoxAction.setEnabled(True)
            self.deleteBoxAction.setEnabled(True)
            self.entireImageAction.setEnabled(True)
            self.newSceneAction.setEnabled(False)
            self.deleteSceneAction.setEnabled(False)
        elif content_type == "scene":
            # self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-scene-hangul.names")
            self.names_file = "SCENE"
            self.name_list = SCENE_LIST
            self.newBoxAction.setEnabled(False)
            self.deleteBoxAction.setEnabled(False)
            self.entireImageAction.setEnabled(False)
            self.newSceneAction.setEnabled(True)
            self.deleteSceneAction.setEnabled(True)
        elif content_type == "landmark":
            # self.names_file = os.path.join(self.names_dir, TARGET_CONTENT.lower() + "-landmark-hangul.names")
            self.names_file = "LANDMARK"
            self.name_list = LANDMARK_LIST
            self.newBoxAction.setEnabled(False)
            self.deleteBoxAction.setEnabled(False)
            self.entireImageAction.setEnabled(False)
            self.newSceneAction.setEnabled(True)
            self.deleteSceneAction.setEnabled(True)
        else:
            # self.names_file = os.path.join(self.names_dir, "idle.names")
            self.names_file = "IDLE"
            self.name_list = IDLE_LIST
            self.newBoxAction.setEnabled(False)
            self.deleteBoxAction.setEnabled(False)
            self.entireImageAction.setEnabled(False)
            self.newSceneAction.setEnabled(False)
            self.deleteSceneAction.setEnabled(False)

        # # Not in list
        # self.name_list = []
        # with open(self.names_file, 'r', encoding='utf-8') as c:
        #     names_strings = c.read()
        # for one_line in names_strings.split('\n'):
        #     splits = one_line.split(',')
        #     if len(splits) == 2:
        #         self.name_list.append(str(splits[1].strip()))
        #     else:
        #         self.name_list.append(str(splits[-1].strip()))
        #
        # print(self.name_list)

        print(" # Content type is {} ({})".format(self.content_type, self.names_file))

        self.process_image()
        self.update_ui()

    def name_dialog_button_action(self):
        try:
            if len(self.img_names) > 0:
                dialog = NameDialog(self)
                dialog.exec_()
        except (TypeError, IndexError):
            self.statusLabel.setText("No Box available")

    def save_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        """Save data back to json file."""
        try:
            # check if the input can be converted to int
            self.update_name_list_ui()

            self.img_json['dataset']['attributes']['answer_refined'] = True

            self.img_json['content'][self.content_type]['annotation']['names'] = self.img_names
            self.img_json['content'][self.content_type]['annotation']['scores'] = self.img_names_scores

            # Turn list of Points back into JSON list
            # TODO scene일 때는 bboxes key 값 수정 자체를 막음
            if self.content_type != 'scene' and self.content_type != 'landmark':
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

            self.statusLabel.setText("저장 완료!")
        except IndexError:
            self.statusLabel.setText("잘못된 정보입니다!")

    def new_box_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        """Add a new box with default size and text."""
        self.img_bboxes.append([Point(0, 0), Point(100, 0), Point(100, 100), Point(0, 100)])
        self.img_names.append("새 컨텐츠 정보")
        self.img_names_scores.append(1.0)

        self.update_name_list_ui()
        self.update_ui()

    def new_scene_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        self.img_names.append("새 컨텐츠 정보")
        self.img_names_scores.append(1.0)

        self.update_name_list_ui()
        self.update_ui()

    def delete_box_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        if len(self.img_bboxes) > 0:
            """Delete current selected bbox."""
            del self.img_bboxes[self.img_bbox_idx]
            del self.img_names[self.img_bbox_idx]
            del self.img_names_scores[self.img_bbox_idx]

            if self.img_bbox_idx == len(self.img_bboxes):
                self.img_bbox_idx -= 1

        self.update_name_list_ui()
        self.update_ui()

    def delete_scene_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

        if len(self.img_names) > 0:
            del self.img_names[self.img_bbox_idx]
            del self.img_names_scores[self.img_bbox_idx]

            if self.img_bbox_idx == len(self.img_bboxes):
                self.img_bbox_idx -= 1

        self.update_name_list_ui()
        self.update_ui()

    def entire_image_action(self):
        """Update all ui elements except lists."""
        if not self.json_files:
            return

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
        """Get new name selection and update UI."""
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
