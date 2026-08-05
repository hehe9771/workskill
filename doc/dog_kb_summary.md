# 狗知识库开源项目调研 - 数据摘要

（从 workflow 转录提取，synthesis agent 失败后主线程综合用）

- 深采项目总数(去重): 115
- 真 dog kb (yes+partial): 74
- 非 dog kb (no): 41
- 不确定 (uncertain): 0
- 核验总数(去重): 51  -> confirmed=50 / refuted=1 / uncertain=0

## 一、真狗知识库 — is_real=yes（专题狗知识库/数据集/工具）

共 54 个


### 类型: dataset (37)

| 名称 | URL | 子领域 | license | 活跃度 | star | 最后更新 | 核验 |
|---|---|---|---|---|---|---|---|
| kabilan03/dogbreedclassification (Dog Breed C | https://www.kaggle.com/datasets/kabilan03/dogbreedclassification | breed | Unknown（Kaggle 元数据标注 lice | stale | 8 upvotes / 107 | 2022-03-14 ( | - |
| ArlingtonCL2/Barkopedia_Dog_Act_Env (Barkoped | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Dog_Act_Env | behavior | MIT | stale | 4 likes (HF数据集用 | 2025-07-08 ( | confirmed |
| ArlingtonCL2/Barkopedia_DOG_AGE_GROUP_CLASSIF | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_DOG_AGE_GROUP_CLASSIFICATION_DATASET | behavior(叫声 vocalization/barks 为主,涉 | MIT | unknown | HuggingFace 指标: | insufficient | - |
| mashequr/images_of_dog_breeds | https://huggingface.co/datasets/mashequr/images_of_dog_breeds | breed | insufficient data (未指定) | stale | 1 like | insufficient | - |
| StanfordExtra | https://github.com/benjiebob/StanfordExtra | general(计算机视觉/动物姿态估计;非behavior/dise | MIT(2024-11-02变更;版权属剑桥大学工 | stale | 113 | 2021-02-01(V | confirmed |
| benjamingray44/inertial-data-for-dog-behaviou | https://www.kaggle.com/datasets/benjamingray44/inertial-data-for-dog-behaviour-classification | behavior | 存疑冲突:数据集描述正文声明"CC BY 4.0" | stale | 13 likes(Kaggle | 2022-01-15(d | confirmed |
| Dog Behavior Location Dataset | https://www.kaggle.com/datasets/kewinowens/dog-behavior-location-dataset | behavior | Unknown | stale | 2 votes (Kaggle | 2025-03-25 | confirmed |
| Dog Emotion Dataset (Cleaned Version) | https://www.kaggle.com/datasets/mohitagarwal17/dog-emotion-datasetcleaned-version | behavior | Apache 2.0 | active | 7 votes / 79 do | 2026-06-20 ( | - |
| subihwang/dogbarkdatasound | https://www.kaggle.com/datasets/subihwang/dogbarkdatasound | behavior | Apache 2.0 | stale | 0 (Kaggle 点赞数=0 | 2023-10-29 ( | confirmed |
| 120 Dog breeds Images for Classification (vik | https://www.kaggle.com/datasets/vikaschauhan734/120-dog-breed-image-classification | breed | Unknown(未指定,Kaggle schema | stale | N/A(Kaggle 无 st | 2023-05-26(d | - |
| Dog Breed Identification (Kaggle) | https://www.kaggle.com/c/dog-breed-identification | breed | Kaggle竞赛规则约束(非标准开源许可),具体条 | archived | N/A(Kaggle无star | 2017(竞赛举办年,已 | confirmed |
| Meta-Album DOG (Dogs Dataset) | https://meta-album.github.io/datasets/DOG.html | breed | Meta-Album 发布版: CC BY-NC  | stale | insufficient da | 2022-12-15 ( | confirmed |
| AtharvaTaras/Dog-Breeds-Dataset | https://github.com/AtharvaTaras/Dog-Breeds-Dataset | breed | CC-BY-4.0 | stale | 11 | 2023-02-02 ( | - |
| Dog Behavior Monitoring Dataset (ziya07) | https://www.kaggle.com/datasets/ziya07/dog-behavior-monitoring-dataset | behavior | CC0: Public Domain | stale | Kaggle无star系统;2 | 2025-04-25 ( | confirmed |
| DogSpeak (DogSpeak_Dataset) | https://huggingface.co/datasets/ArlingtonCL2/DogSpeak_Dataset | behavior (vocalization / bioacousti | CC BY-NC-SA 4.0 (Creative | active (月下载 16  | 7 likes / 25 fo | README 关联 20 | confirmed |
| mashequr/dog_breed_images | https://huggingface.co/datasets/mashequr/dog_breed_images | breed | 未标注(Not specified) | stale | 0 likes(HF无star | 2024-07-28(l | - |
| Stanford Dogs Dataset | http://vision.stanford.edu/aditya86/ImageNetDogs/main.html | breed | insufficient data (页面与REA | archived | insufficient da | insufficient | confirmed |
| Dog10K | https://dog10k.kiz.ac.cn/ | breed | insufficient data (首页未标注许 | active | N/A (非 GitHub 仓 | 2024-10-22 发 | confirmed |
| ArlingtonCL2/Barkopedia_Individual_Dog_Recogn | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Individual_Dog_Recognition_Dataset | behavior/vocalization (bark audio), | MIT | stale | 0 (HF likes) | insufficient | - |
| fishchen/dog-behavior-dataset | https://huggingface.co/datasets/fishchen/dog-behavior-dataset | behavior (视频行为数据, 倾向 pose/姿态识别) | insufficient data (页面未声明  | stale (月下载 3, 0 | 0 likes (Huggin | 最近一次上传约 2 个月 | confirmed |
| juniorrios/icomp-dog-breed | https://huggingface.co/datasets/juniorrios/icomp-dog-breed | breed | insufficient data(页面未标注 l | stale | 1 like, 59 down | 2023-06-15 | refuted |
| benni-ben/dog-breeds | https://huggingface.co/datasets/benni-ben/dog-breeds | breed (品种分类/识别) | MIT | unknown | 1 (likes) | insufficient | - |
| Dewa/Dog_Emotion_Dataset_v2 | https://huggingface.co/datasets/Dewa/Dog_Emotion_Dataset_v2 | behavior (emotion classification) | creativeml-openrail-m (页面 | stale | 6 likes | 2024-04-10 ( | - |
| Barkopedia_Dog_Sex_Classification_Dataset | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Dog_Sex_Classification_Dataset | behavior(vocalization/barking) + bi | MIT | unknown(无更新日期,下 | 0 likes; 20 dow | insufficient | confirmed |
| lurnake/dog-breed-traits-data | https://github.com/lurnake/dog-breed-traits-data | breed/behavior/general(品种分组+性格行为+生活 | 非标准"open-source principle | stale | 0 | 2025-02-13 | - |
| Dog Behavior Object Detection Dataset (Robofl | https://universe.roboflow.com/carl-m6y6w/dog-behavior-qwvgf | behavior | insufficient data | unknown | N/A (Roboflow U | insufficient | - |
| gsusI/dog-breeds-database | https://github.com/gsusI/dog-breeds-database | breed | CC BY-NC 4.0 (Creative Co | stale | 0 | 2026-04-14 ( | - |
| Kaggle Dog Behavior Analysis Dataset (arashni | https://www.kaggle.com/datasets/arashnic/animal-behavior-analysis | behavior | CC BY-SA 4.0 | stale | N/A(Kaggle数据集,无 | 2022-06-25(v | confirmed |
| Dog Aging Project (DAP) | https://dogagingproject.org/data-access | general | 无开源 license;数据受 DAP Data  | active | 16 | 数据集每年发布一次(最新 | confirmed |
| umuttuygurr/videosdog (Real-World Dog Behavio | https://www.kaggle.com/datasets/umuttuygurr/videosdog | behavior | CC0: Public Domain | active | 3 (votes/likes) | 2025-12-09 ( | - |
| Morevorot/Dog_breed_Japanese_Spitz | https://huggingface.co/datasets/Morevorot/Dog_breed_Japanese_Spitz | breed | cc-by-sa-4.0 (WebFetch提取; | stale | 0 likes (HF用lik | insufficient | - |
| waqi786/dogs-dataset-3000-records (Kaggle) | https://www.kaggle.com/datasets/waqi786/dogs-dataset-3000-records | breed | Apache 2.0 | stale | 31 (likes); 225 | 2024-07-30 ( | confirmed |
| ArlingtonCL2/Barkopedia-Dog-Vocal-Detection | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia-Dog-Vocal-Detection | behavior (vocalization) + breed | 未在页面明确标注 (unspecified) | active (有持续下载量3 | 3 likes; 346 do | insufficient | confirmed |
| Dog voice emotion dataset (Demo-Lite) | https://www.kaggle.com/datasets/shivarao100/dog-voice-emotion-dataset | behavior (情绪/发声 emotion & vocalizat | Apache 2.0 | stale | 9 (Kaggle upvot | 2024-09-14 ( | - |
| paiv/fci-breeds | https://github.com/paiv/fci-breeds | breed | MIT | active | 48 | 2025-12-06(r | confirmed |
| Movement Sensor Dataset for Dog Behavior Clas | https://data.mendeley.com/datasets/vxhx934tbn/1 | behavior | CC BY 4.0 | stale | N/A (Mendeley D | 2021-07-02 ( | - |
| American-Kennel-Club-Breeds-by-Size-Dataset | https://github.com/MeganSorenson/American-Kennel-Club-Breeds-by-Size-Dataset | breed | 无(license: null,未声明许可证,默认 | stale | 8 | 代码最后推送 2021- | - |

### 类型: mixed (10)

| 名称 | URL | 子领域 | license | 活跃度 | star | 最后更新 | 核验 |
|---|---|---|---|---|---|---|---|
| Dog Knowledge Graph (pranjal-y4/Knowledge_Gra | https://github.com/pranjal-y4/Knowledge_Graph | ontology(横跨breed/disease-health/tra | 无(仓库未含LICENSE文件,repo页未声明许 | stale(单日突发式3次上传 | 0 | 2026-02-18(全 | - |
| jthorvaldur/bulldogs (BulldogDerm / The Bulld | https://github.com/jthorvaldur/bulldogs | disease (dermatology/skin health) | 未标注 (README与repo页均无licens | active | 0 | 最近更新(repo页"l | confirmed |
| iDog | https://ngdc.cncb.ac.cn/idog/ | general(综合:品种/疾病/表型/行为/基因组/本体;横向覆盖多 | 数据库内容"仅限学术免费使用"(free for  | active | insufficient da | 2025-01(iDog | confirmed |
| 729r2pzfqs-ux/breed-guide (BreedFinder) | https://github.com/729r2pzfqs-ux/breed-guide | breed(主);部分覆盖 behavior(temperament  | insufficient data(仓库主页未注明 | unknown(672 次提交 | 0 | insufficient | confirmed |
| iDog Processing Pipelines (Br1anChou/idog) | https://github.com/Br1anChou/idog | general(犬科多组学/基因组学,覆盖品种/疾病/行为/形态/驯化 | MIT | unknown | 4 | insufficient | confirmed |
| tom-sims/ManyDogs-Project-Analysis-of-Pet-Dog | https://github.com/tom-sims/ManyDogs-Project-Analysis-of-Pet-Dog-Behaviour-and-C-BARQ-Scores | behavior | 未列出(无 License) | stale | 1 | insufficient | - |
| DucNgn/Dog-Facts-API-v2 | https://github.com/DucNgn/Dog-Facts-API-v2 | general | MIT | stale | 5 | insufficient | - |
| Deep-Learning-Fine-Grained-Action-Recognition | https://github.com/samtwl/Deep-Learning-Fine-Grained-Action-Recognition-Canine-Behavior | behavior | No license specified | stale | 2 | insufficient | confirmed |
| Dog Breed Ontology (Tetherless-World / RPI OE | https://tetherless-world.github.io/ontology-engineering/oe2022/dog-breed-ontology/related_work.html | breed / ontology (品种特征建模与推荐,非行为/疾病/ | MIT License (页面 license.h | stale | 13 (注:为整个 ontol | 约 2022-11 (F | confirmed |
| imixiu/paws-tales (Paws&Tales) | https://github.com/imixiu/paws-tales | general(覆盖 care/training/behavior/h | 未声明(仓库无 LICENSE 文件) | active(线上站 paws | 0 | insufficient | confirmed |

### 类型: doc-kb (5)

| 名称 | URL | 子领域 | license | 活跃度 | star | 最后更新 | 核验 |
|---|---|---|---|---|---|---|---|
| consigcody94/calm-hound (Calm Hound) | https://github.com/consigcody94/calm-hound | behavior/training (狗分离焦虑 separation | 未标注(not specified,无 LICEN | stale/unknown(单 | 0 | insufficient | confirmed |
| Stanford-Dogs-OWL-Ontology | https://github.com/miranthajayatilake/Stanford-Dogs-OWL-Ontology | breed/ontology | 无 (repo 未声明任何 license) | stale | 1 | 2021-02 (本体  | - |
| CeruleanBeaver/awesome-dogs | https://github.com/CeruleanBeaver/awesome-dogs | general | CC0-1.0 (Creative Commons | stale | 0 | 2023-06-02 ( | - |
| FengChen-406/dog-knowledge-base | https://github.com/FengChen-406/dog-knowledge-base | general (care/breed/training/health | MIT | stale | 1 | 2024 (仅 1 次  | - |
| leelaunches/holihounds | https://github.com/leelaunches/holihounds | general (dog-friendly travel/accomm | insufficient data (README | unknown | 0 | main 分支共 11  | - |

### 类型: tool (1)

| 名称 | URL | 子领域 | license | 活跃度 | star | 最后更新 | 核验 |
|---|---|---|---|---|---|---|---|
| Dog API (kinduff/dogapi.dog) | https://github.com/kinduff/dogapi.dog | breed(犬种为主;含groups与fun facts,无行为/疾病 | MIT | active(83 commi | 176 | May 18(年份未确认 | confirmed |

### 类型: code (1)

| 名称 | URL | 子领域 | license | 活跃度 | star | 最后更新 | 核验 |
|---|---|---|---|---|---|---|---|
| c840264221/dog-knowledge-rag | https://github.com/c840264221/dog-knowledge-rag | breed（犬种百科为主，含 breed-specific 行为/性格 | MIT | active | 0 | 2026-07-05（最 | - |

## 二、部分相关狗知识库 — is_real=partial（含狗的通用/边缘项目）

共 20 个


### 类型: mixed (7)

| 名称 | URL | 子领域 | license | 活跃度 | star | 核验 |
|---|---|---|---|---|---|---|
| Sujimirutikaa/Pet-Care-Advisor | https://github.com/Sujimirutikaa/Pet-Care-Advisor | disease/care | MIT | stale | 0 | - |
| Vertebrate Breed Ontology (VBO) | https://github.com/monarch-initiative/vertebrate-breed-ontology | ontology/breed | CC-BY 4.0 | active | 16 | confirmed |
| JackyeC/keep-waco-wagging | https://github.com/JackyeC/keep-waco-wagging | general | 无(未声明 license,无 LICENSE 文 | active | 0 | - |
| Mammalian Phenotype Ontology (MP) | https://github.com/mgijax/mammalian-phenotype-ontology | ontology | CC-BY-4.0 (主页显示;README未提及 | active | 20 | confirmed |
| Liuyangpai (遛养派) | https://www.19up.com/about | behavior+breed+genetics/neuroscienc | 未提及(闭源商业平台,无开源许可;仅有闽ICP备2 | active | N/A(非GitHub仓库,为 | confirmed |
| Dog Translator Behavior Dictionary (狗语翻译器 - 狗 | https://dogtranslator.org/zh/dictionary.html | behavior | insufficient data (非开源项目, | unknown (商业站点,无 | N/A (非 GitHub r | confirmed |
| artuguen28/PawAid-AI | https://github.com/artuguen28/PawAid-AI | care (first-aid/emergency/toxicolog | MIT | stale | 0 | confirmed |

### 类型: dataset (7)

| 名称 | URL | 子领域 | license | 活跃度 | star | 核验 |
|---|---|---|---|---|---|---|
| ewwerpm/dog_no_barking | https://huggingface.co/datasets/ewwerpm/dog_no_barking | behavior | insufficient data（未指定） | stale | 0 likes | - |
| feiwu77777/animime-dog-breeds | https://huggingface.co/datasets/feiwu77777/animime-dog-breeds | breed | Research / non-commercial | stale | 0 | - |
| Animal Veterinary Health Dataset (sathwiknomu | https://www.kaggle.com/datasets/sathwiknomula/animal-veterinary-health-dataset | disease (妊娠相关疾病:Brucellosis/Toxopla | CC BY-SA 4.0 (https://cre | active (2025-08 | 2 likes (Kaggle | - |
| lpastor75/dog-breed-classification | https://huggingface.co/datasets/lpastor75/dog-breed-classification | breed | 未标注(not specified) | stale | 1 like | - |
| Oxford-IIIT Pet Dataset (VGG) | https://www.robots.ox.ac.uk/~vgg/data/pets/ | breed | Creative Commons Attribut | archived | N/A (非GitHub仓库, | confirmed |
| VetDataHub | https://github.com/Vetdatahub/VetDataHub | general (多物种兽医综合目录); 犬部分覆盖 breed(品种 | MIT (仓库根 LICENSE 为 MIT);R | unknown (21 com | 44 | confirmed |
| Pet Health Symptoms Dataset (yyzz1010) | https://www.kaggle.com/datasets/yyzz1010/pet-health-symptoms-dataset | disease | MIT | stale | 3 likes (Kaggle | - |

### 类型: doc-kb (2)

| 名称 | URL | 子领域 | license | 活跃度 | star | 核验 |
|---|---|---|---|---|---|---|
| PrimPetCare (syedazobiarizvi-sudo/primpetcare | https://github.com/syedazobiarizvi-sudo/primpetcare.github.io | general/care | insufficient data (仓库未指定  | stale | 0 | confirmed |
| daisy-kyushu/daisy-kyushu-dog-guide | https://github.com/daisy-kyushu/daisy-kyushu-dog-guide | general(旅行/生活指南;含 care 护理、breed 萨摩耶 | 无(未在 README/仓库中指定) | active | 1 | confirmed |

### 类型: code (2)

| 名称 | URL | 子领域 | license | 活跃度 | star | 核验 |
|---|---|---|---|---|---|---|
| Jofleming/canine_disease_prediction | https://github.com/Jofleming/canine_disease_prediction | disease | 无/未指定(Public 仓库但无 LICENSE | stale | 0 | - |
| GuidePaw | https://github.com/jphutching/GuidePaw | training | No license (unlicensed,仓库 | active | 1 | confirmed |

### 类型: tool (2)

| 名称 | URL | 子领域 | license | 活跃度 | star | 核验 |
|---|---|---|---|---|---|---|
| dog-behavior-dataset-creation-tools | https://github.com/giovanni-gallerani/dog-behavior-dataset-creation-tools | behavior | CC-BY-4.0 | stale | 0 | - |
| dog-ceo-api (Dog CEO API) | https://github.com/ElliottLandsborough/dog-ceo-api | breed | MIT | active | 712 | confirmed |

## 三、证伪项目（核验 verdict=refuted）

共 1 个

| 名称 | URL | 核验结论 | is_real | 证据 |
|---|---|---|---|---|
| juniorrios/icomp-dog-breed | https://huggingface.co/datasets/juniorrios/icomp-dog-breed | refuted | no | 独立 WebFetch 三角度(主页面/README/文件树)核验结果:

【元数据全部确认,无夸大】
- type=dataset ✓,Modality=Image,Format=imagefolder,Size=724 MB,Rows= |

## 四、核验全部明细（confirmed/refuted/uncertain）

共 51 个

| 名称 | URL | verdict | is_real | 证据摘要 |
|---|---|---|---|---|
| TugaYousif/dog_breeds | https://huggingface.co/datasets/TugaYousif/dog_breeds | confirmed | no | 四角度独立核验全部一致,深采结论准确,无夸大无不符。

1. 是否狗知识库: 否。从文件树(api/datasets/.../tree/main)看,全仓仅 3 个文件——.gitattributes |
| johananoa/dog_breed_images | https://huggingface.co/datasets/johananoa/dog_breed_images | confirmed | no | 独立四角度抓取(主页/tree/main/commits/main/README raw)全部成功并相互印证,深采结论完全坐实。

1) 是否"关于狗的知识库/数据集":否。主页明确标注"No dat |
| artuguen28/PawAid-AI | https://github.com/artuguen28/PawAid-AI | confirmed | no | 独立重抓主仓库页、README、data/、src/、scripts/、app/、docs/ 目录及 commits 页,深采结论实质事实全部成立,无法推翻。逐项核验:

【1. 非狗知识库——确认】 |
| iDog Processing Pipelines (Br1anChou/ido | https://github.com/Br1anChou/idog | confirmed | yes | 独立从 releases/issues/commits/主目录树/LICENSE/reference 目录/NAR 论文 6 个不同角度重抓,深采结论整体属实,无营销夸大。

1) 是否真为"狗的知识 |
| Liuyangpai (遛养派) | https://www.19up.com/about | confirmed | partial | 独立重抓 /about、/、/methodology、/research/community、/citation-guidelines 五个路径,逐项核验深采结论与三大矛盾,结论:深采的 partia |
| dog-ceo-api (Dog CEO API) | https://github.com/ElliottLandsborough/dog-ceo-api | confirmed | partial | 独立换路径重抓(commits页/repo主页/raw composer.json/raw readme.md/src目录)核验深采结论,四项核心判定全部坐实,未发现夸大/伪造,深采甚至偏保守。

1 |
| Meta-Album DOG (Dogs Dataset) | https://meta-album.github.io/datasets/DOG.html | confirmed | yes | 核心结论全部坐实,但 star 字段推理有误,特纠正。

【确为真实犬类数据集,非文本知识库】4 来源交叉证实:DOG 主页、Meta-Album 主站、OpenML JSON API(三版本全量)、 |
| Dog Aging Project (DAP) | https://dogagingproject.org/data-access | confirmed | yes | 独立重抓佐证深采结论,核心事实全部核实通过。

【1. 真为狗知识库/数据集——确认】
- 数据浏览器 data.dogagingproject.org 明确自称"the most ambitious |
| jthorvaldur/bulldogs (BulldogDerm / The  | https://github.com/jthorvaldur/bulldogs | confirmed | yes | 独立重抓repo主页+commits+源码目录(data/viz/site)+raw conditions.json+handbook.html+渲染README blob，与深采结论双向印证，核心判 |
| kinduff/dogapi.dog (The Dog API) | https://github.com/kinduff/dogapi.dog | confirmed | yes | 独立多角度复核,深采结论全部通过,无推翻性证据。

【1. 项目性质—确认真实狗知识库/数据API】GitHub 描述原文:"Provides information on over 340 dog  |
| benjamingray44/inertial-data-for-dog-beh | https://www.kaggle.com/datasets/benjamingray44/inertial-data-for-dog-behaviour-classification | confirmed | yes | 独立重抓 Kaggle 页面 raw HTML 内嵌 schema.org Dataset JSON-LD + Mendeley 原始源 citation 元数据,双重交叉核验深采结论全部成立。

1 |
| iDog | https://ngdc.cncb.ac.cn/idog/ | confirmed | yes | 独立重抓多角度佐证,深采结论准确,无营销夸大。

【1. 确为犬类知识库(非图片分类器/非通用动物库/非同名无关项目)】
- 主页 https://ngdc.cncb.ac.cn/idog/ 确认为  |
| ArlingtonCL2/Barkopedia-Dog-Vocal-Detect | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia-Dog-Vocal-Detection | confirmed | yes | 独立重抓主页面+README+文件树+commit历史四源,证据相互印证,深采结论准确。

1) 真为狗专用数据集: README/页面明确为"dog vocalization detection", |
| StanfordExtra | https://github.com/benjiebob/StanfordExtra | confirmed | yes | 独立换路径重抓(仓库根目录结构/commits历史/releases/LICENSE raw文件, 均非深采agent已抓路径)后, 深采结论全部可证实, 无营销夸大。

1) 是否真为狗专用数据集( |
| Kaggle Dog Behavior Analysis Dataset (ar | https://www.kaggle.com/datasets/arashnic/animal-behavior-analysis | confirmed | yes | 独立重抓三个来源(Kaggle API view 元数据、API list 文件列表、网页本体)交叉核验,深采核心结论全部坐实,仅有一处表述可澄清。

【一、确为狗数据集 — 坐实】
- API vi |
| FuTRES Ontology of Vertebrate Traits (FO | https://github.com/futres/fovt | confirmed | no | 六源独立交叉核验(主仓页/master README/project.yaml/releases/issues/futres.org 主站)确认深采结论在所有实质点准确。

【非狗 KB 确认】REA |
| Dog Behavior Monitoring Dataset (ziya07) | https://www.kaggle.com/datasets/ziya07/dog-behavior-monitoring-dataset | confirmed | yes | 独立重抓两个 Kaggle 公开 API 端点(/api/v1/datasets/view/ 与 /api/v1/datasets/list/)交叉验证,深采结论全部字段精确吻合,无夸大、无不符。

 |
| imixiu/paws-tales (Paws&Tales) | https://github.com/imixiu/paws-tales | confirmed | partial | 独立重抓 GitHub 仓库页/releases/issues/commits/tree/app/lib 目录、raw AGENTS.md/package.json、线上 sitemap.xml/au |
| monarchwebsolutions/dog-grief-guide-them | https://github.com/monarchwebsolutions/dog-grief-guide-theme | confirmed | no | 独立重抓(主仓库页+releases+issues+commits+templates目录)全部成功,与深采结论完全一致,无夸大。

1) 类型核验:仓库结构为标准 Shopify 主题目录(asse |
| juniorrios/icomp-dog-breed | https://huggingface.co/datasets/juniorrios/icomp-dog-breed | refuted | no | 独立 WebFetch 三角度(主页面/README/文件树)核验结果:

【元数据全部确认,无夸大】
- type=dataset ✓,Modality=Image,Format=imagefold |
| Dog Translator Behavior Dictionary (狗语翻译 | https://dogtranslator.org/zh/dictionary.html | confirmed | partial | 独立三路抓取(WebFetch 渲染、WebFetch 首页、mcp__fetch__fetch 原始 HTML)+ robots.txt 互相印证,深采结论实质成立,未能推翻。

1) 内容范围一致 |
| PrimPetCare | https://github.com/syedazobiarizvi-sudo/primpetcare.github.io | confirmed | no | 独立重抓(源码 tree/main + 主页 + commits + releases + issues + raw README)全部成功并交叉印证,深采结论核心成立,数值维度全准。

【维度1:是 |
| subihwang/dogbarkdatasound | https://www.kaggle.com/datasets/subihwang/dogbarkdatasound | confirmed | partial | 独立重抓 Kaggle 原始 HTML，成功获取页面内嵌的权威 JSON-LD(schema.org Dataset)元数据，逐项核验深采结论：

【全部量化事实精确匹配】
- interaction |
| Vertebrate Breed Ontology (VBO) | https://github.com/monarch-initiative/vertebrate-breed-ontology | confirmed | partial | 独立四路抓取(releases page1+page2、issues、OBO Foundry官方页、mcp__fetch__fetch原始主页含README)交叉证实深采结论,无重大矛盾。

1) 是 |
| egoose/dog_breeds_181 | https://huggingface.co/datasets/egoose/dog_breeds_181 | confirmed | no | 独立对抗核验(换角度: HuggingFace API 结构化元数据 + 文件树 + 用户主页 + 同名邻近仓库)三向一致,确认深采结论准确,无夸大/不符。

证据1 — API 元数据(/api/d |
| Movement Sensor Dataset for Dog Behavior | https://data.mendeley.com/datasets/vxhx934tbn | confirmed | yes | 核心身份判定 CONFIRMED,但深采的 activity=stale 被推翻,另有2处小瑕疵。

【1. 确为犬类行为数据集 — 强交叉佐证,非图片分类器/通用动物库/同名无关项目】
三路独立来源 |
| BAAI-DataCube Dog-Dataset (ModelScope) | https://modelscope.cn/datasets/BAAI/BAAI-DataCube_Dog-Dataset | confirmed | no | 独立重抓核实：深采结论核心判断【confirmed】，但部分佐证措辞有瑕疵（不影响结论）。

【证伪要点 — 三重独立信号】
1. ModelScope 数据集详情 API（权威源）返回 HTTP 4 |
| DogSpeak (DogSpeak_Dataset) | https://huggingface.co/datasets/ArlingtonCL2/DogSpeak_Dataset | confirmed | yes | 独立 WebFetch 多角度重抓,深采结论全部核实无误,无夸大。

【1. 真实狗数据集 - 是】HuggingFace 卡片自述"a large-scale canine vocalization |
| Oxford-IIIT Pet Dataset (VGG) | https://www.robots.ox.ac.uk/~vgg/data/pets/ | confirmed | partial | 三源独立交叉佐证,深采结论全部坐实,无夸大/不符。(1) 主页 https://www.robots.ox.ac.uk/~vgg/data/pets/ WebFetch 成功:逐字引述"We have |
| Dog Breed Ontology (Tetherless-World / R | https://tetherless-world.github.io/ontology-engineering/oe2022/dog-breed-ontology/related_work.html | confirmed | yes | 独立核验(走深采 agent 未走的路径:GitHub 源码目录页、仓库主页 HTML、master 分支文件列表)全部证实深采结论,无实质性夸大。

【1. 真为狗知识库】✓ confirmed。r |
| sissc0731/dog-care-guide | https://github.com/sissc0731/dog-care-guide | confirmed | no | 独立重抓 10 条路径核验，深采结论 is_real_dog_kb=no 完全成立，且证据更强。逐项核验如下：

1) 仓库主页 github.com/sissc0731/dog-care-guide |
| 729r2pzfqs-ux/breed-guide (BreedFinder) | https://github.com/729r2pzfqs-ux/breed-guide | confirmed | yes | 核心结论(真实狗知识库/数据集)经独立重抓完全证实,但 activity=unknown 一项被推翻(实为 active)。

【证实项】
1. 真实狗知识库(非图片分类器/非通用动物库/非同名无关项 |
| VetDataHub | https://github.com/Vetdatahub/VetDataHub | confirmed | no | 核心结论经独立重抓证实,但有两处修正。

【证实项】
1. star=44 ✓(主页 star 按钮显示 44;另 fork=9,watchers=5,license=MIT,未归档)。深采 star |
| Barkopedia_Dog_Sex_Classification_Datase | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Dog_Sex_Classification_Dataset | confirmed | yes | 核心结论全部坐实,仅activity字段"无更新日期"表述有轻微事实偏差(不影响总体判定)。

【已确认项】
1. 真狗数据集(非图片分类器/非通用动物库/非同名无关项目):README原文"29,3 |
| daisy-kyushu/daisy-kyushu-dog-guide | https://github.com/daisy-kyushu/daisy-kyushu-dog-guide | confirmed | partial | 独立 WebFetch 三路交叉验证（GitHub API 路径 403，改用网页路径主页+tree/main源码目录+releases页全部成功）。证据如下：

1. 仓库元数据（github.co |
| Calm Hound | https://github.com/consigcody94/calm-hound | confirmed | partial | 独立重抓全部成功,深采结论的事实性主张逐项核实无误。

【狗主题核实】确为狗相关文档站。仓库描述"free, force-free guides for dog separation anxiety" |
| Dog Breed Identification (Kaggle) | https://www.kaggle.com/c/dog-breed-identification | confirmed | yes | 独立重抓多路径核验，结论与深采一致，无夸大。

【直接抓取 Kaggle】独立抓取 https://www.kaggle.com/c/dog-breed-identification、/leaderb |
| matveyashikhin/VetDoc_AI | https://github.com/matveyashikhin/VetDoc_AI | confirmed | no | 独立重抓多角度(主页、commits、releases、issues、branches、raw README、用户 profile、API)全部与深采结论一致,无推翻迹象。

1) 是否"关于狗的知识 |
| Mariptime/DogBreeds | https://huggingface.co/datasets/Mariptime/DogBreeds | confirmed | no | 独立重抓四条路径(HF API 元数据、/tree/main 文件树、/raw/main/README.md、渲染页 HTML)全部与深采结论一致,证据互相印证,未发现任何夸大或不符。

1) 是否真 |
| Mammalian Phenotype Ontology (MP) | https://github.com/mgijax/mammalian-phenotype-ontology | confirmed | no | 独立换角度(/releases、/issues、/tree/master/src、raw README、raw LICENSE、blob 页侧栏)交叉核实,深采结论基本准确,且其"夸大犬类覆盖"的怀疑 |
| Deep-Learning-Fine-Grained-Action-Recogn | https://github.com/samtwl/Deep-Learning-Fine-Grained-Action-Recognition-Canine-Behavior | confirmed | partial | 独立WebFetch重抓(默认分支实为master,非main;README与code目录在main分支404,印证深采未抓master路径)逐项核实结论:

【1. 主题真实性 - 确认是犬类项目, |
| paiv/fci-breeds | https://github.com/paiv/fci-breeds | confirmed | yes | 通过 5 个独立路径核验(releases页/源码目录树/issues页/commits页/demo站点),深采结论全部属实。

1. 真实性确认:该项目是 FCI(Fédération Cynolo |
| Dog Behavior Location Dataset | https://www.kaggle.com/datasets/kewinowens/dog-behavior-location-dataset | confirmed | yes | 独立从 5 条路径交叉核实,深采结论所有关键数据点均无误,维持 is_real_dog_kb=yes。

【1. 确为狗相关数据集,非同名/无关项目】
- Kaggle API v1 datasets |
| GuidePaw | https://github.com/jphutching/GuidePaw | confirmed | no | 独立重抓 GitHub 主页 + tree/HEAD 源码树 + releases + issues + docs/ 目录 + sql/migrations/ + raw README 全文 + ra |
| Stanford Dogs Dataset | http://vision.stanford.edu/aditya86/ImageNetDogs/main.html | confirmed | partial | 独立重抓 main.html + README.txt + 目录 + LICENSE(404) 全部成功，深采事实性结论逐项吻合：120品种/20,580张图片/类别标签+边界框标注/源自ImageN |
| Dog10K | https://dog10k.kiz.ac.cn/ | confirmed | yes | 独立重抓首页 + NAR 2024 论文(DOI 10.1093/nar/gkae928, PMID 39436034)双重交叉核验,未能推翻深采结论,全部坐实。

【1. 真实性-确为犬类多组学知识 |
| fishchen/dog-behavior-dataset | https://huggingface.co/datasets/fishchen/dog-behavior-dataset | confirmed | yes | 独立抓取 8 个来源(HF API JSON、主页、README raw、文件树、data目录、dogspose Space、metadata.jsonl 实际内容、用户主页)核验。

【印证属实】( |
| waqi786/dogs-dataset-3000-records | https://www.kaggle.com/datasets/waqi786/dogs-dataset-3000-records | confirmed | partial | 独立换用 Kaggle 官方 API (https://www.kaggle.com/api/v1/datasets/view/waqi786/dogs-dataset-3000-records 返回 |
| Stanford Dogs Dataset (Kaggle mirror by  | https://www.kaggle.com/datasets/jessicali9530/stanford-dogs-dataset | confirmed | no | 独立双源核验,深采结论全部事实性陈述为真,无夸大/不符。

【源1:Kaggle raw HTML 内嵌 JSON-LD schema.org Dataset】(独立复现深采方法,字段全量匹配)
-  |
| ncreighton/veterinary--animal-care-knowl | https://github.com/ncreighton/veterinary--animal-care-knowledge-base-and-wiki-discord-bot | confirmed | no | 独立重抓5个角度(主页/README/commits/raw main.py/releases)全部佐证深采结论,核心判定is_real_dog_kb=no完全成立。

【1. 不是狗知识库——完全确 |
| ArlingtonCL2/Barkopedia_Dog_Act_Env | https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Dog_Act_Env | confirmed | partial | 独立换角度重抓（README原始文件 resolve/main/README.md、文件树 tree/main、组织页 ArlingtonCL2、数据集卡片）四路交叉核验，深采核心结论全部成立，仅1处 |

## 五、真狗知识库内容范围详情（content_scope 全文）


### kabilan03/dogbreedclassification (Dog Breed Classification) 
- URL: https://www.kaggle.com/datasets/kabilan03/dogbreedclassification
- 类型: dataset | 子领域: breed | is_real: yes
- license: Unknown（Kaggle 元数据标注 license name=Unknown，无 URL） | 活跃: stale | star: 8 upvotes / 1078 downloads / 8264 views / 0 comments | 更新: 2022-03-14 (dateModified: 2022-03-14T17:49:54.457Z, version 3)
- 内容范围: 狗品种图像分类数据集：93 个不同狗品种，共 6391 张训练图 + 762 张验证图 + 887 张测试图（带标签），zip 打包约 285MB。可用于动物检测和狗品种分类任务。仅含图像及标签，无行为/疾病/饲养/训练等知识文本。
- 备注: 确为狗品种图像分类数据集，描述与实际一致，无营销夸大。证据来自 Kaggle 页面内嵌的 schema.org Dataset JSON-LD 元数据（非 JS 渲染后的 DOM）。规模与影响力均一般：93 品种/约 8000 张图/285MB，8 个赞/1078 下载，最后更新于 2022-03 已逾 3 年未维护，作为对比报告非重点。仅含图像+标签，非知识库/文档型，不适合作为"狗知识库"重点对比项。下载需 Kaggle 登录（requiresSubscription=true，但 isAccessibleForFree=true）。无对应 GitHub 仓库 README 可抓（Kagg

### Dog API (kinduff/dogapi.dog) 
- URL: https://github.com/kinduff/dogapi.dog
- 类型: tool | 子领域: breed(犬种为主;含groups与fun facts,无行为/疾病/饲养/训练) | is_real: yes
- license: MIT | 活跃: active(83 commits,1 open issue,21 PRs,GitHub Actions已配置) | star: 176 | 更新: May 18(年份未确认;commits页被robots.txt屏蔽,GitHub API返回403无法精确核实)
- 内容范围: 犬种信息(breeds):340+犬种详细资料;犬种分组(breed groups):20个犬种组;趣闻(fun facts)。不覆盖行为(behavior)/疾病(disease)/饲养(care)/训练(training)。数据存储在PostgreSQL中,通过Rails API对外提供,含Swagger文档。
- 备注: 核实结论:确为真实的狗知识库/API,与已知描述(340+犬种、Ruby on Rails+PostgreSQL)完全吻合。

抓取情况(fetch_status=partial):
1. dogapi.co 主站本身无法访问(WebFetch socket closed、mcp__fetch__fetch connection issue),无法确认API线上是否仍可调用;
2. GitHub repo页(github.com/kinduff/dogapi.dog)成功抓取,提取到description/语言占比/stars/license/技术栈/内容范围;
3. raw README(H

### ArlingtonCL2/Barkopedia_Dog_Act_Env (Barkopedia Challenge Dataset) 
- URL: https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Dog_Act_Env
- 类型: dataset | 子领域: behavior | is_real: yes
- license: MIT | 活跃: stale | star: 4 likes (HF数据集用"likes"非star;另 downloads last month=134) | 更新: 2025-07-08 (组织页显示Updated Jul 8, 2025;最后一次commit为"Test Data Released"约12个月前;今日2026/07/06,近一年无更新)
- 内容范围: 狗叫声音频数据集,聚焦从吠叫声理解狗的"活动(activity)"与"环境(environment)"。活动类别(act_category)8类:rest(休息)、alerting to sounds(对声音警示)、seeking attention(寻求注意)、playing with human(与人玩)、playing with other animals(与其他动物玩)、playing with toy(玩玩具)、begging for food(乞食)、taking shower(洗澡)。环境类别(env_category)6类:indoor general(室内一般)、near window(窗边)、near door(门边)、on grass(草地上)、near other animals(近其他动物)、vehicle interior(车内)。标注方式:先用视觉-语言模型(Janus-Pro-7B)做视频辅助推断生成,再人工核验。非文本知识库/文档,而是带标签的音频分类数据集,属行为+环境感知维度。
- 备注: 核实结论:确为真实狗数据集,HuggingFace托管,Arlington Computational Linguistic Lab发布,MIT协议,746MB,属Barkopedia挑战系列(该组织共10个数据集,8个带Barkopedia前缀,涵盖品种/年龄/性别/个体识别/情绪/发声检测/活动环境/发声分离等任务)。

【重大描述纠错】已知描述"约134样本"错误。"134"实为HF页面"Downloads last month:134"(月下载量),非样本数。真实样本数=15,600条狗吠音频(训练集12,480 + 测试集3,120,其中测试集40%公开1,248条用于排行榜、60%

### c840264221/dog-knowledge-rag 
- URL: https://github.com/c840264221/dog-knowledge-rag
- 类型: code | 子领域: breed（犬种百科为主，含 breed-specific 行为/性格描述；不含 disease/care/training/ontology） | is_real: yes
- license: MIT | 活跃: active | star: 0 | 更新: 2026-07-05（最新 release v1.7.5"断点恢复MVP"；共 30 个 release、35 commits）
- 内容范围: 基于 RAG 的狗百科智能问答系统。数据源为 AKC（美国犬业俱乐部）官网犬种页面，经 Selenium 爬取后结构化为 Markdown 知识库，再经 HuggingFace Embedding + Chroma 向量库 + CrossEncoder Reranker + LLM 实现问答。内容仅覆盖犬种百科：犬种性格(temperament)、特征、品种特质，支持中英文犬种别名映射（如"金毛→Golden Retriever"）。不覆盖疾病/兽医、饲养护理、训练、营养、本体等方向。Demo 示例为"Afghan Hound 性格怎么样"。属个人/面试作品（README 含"面试亮点"小节）。
- 备注: 三次独立抓取（WebFetch repo 页 + WebFetch raw README + mcp__fetch__fetch 原始 HTML）结果完全一致，无矛盾。确为真实狗知识库（RAG 问答系统，非图片分类器/通用动物/同名无关项目）。技术栈：Python + LangChain(LCEL) + Chroma + HuggingFace Embedding + CrossEncoder Reranker + Selenium。架构亮点：结构化过滤+向量检索混合、Markdown 标题层级语义切块、Alias 语义映射、Reranker 二阶段精排、模型懒加载+本地缓存。不作为对比报告重

### ArlingtonCL2/Barkopedia_DOG_AGE_GROUP_CLASSIFICATION_DATASET 
- URL: https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_DOG_AGE_GROUP_CLASSIFICATION_DATASET
- 类型: dataset | 子领域: behavior(叫声 vocalization/barks 为主,涉及 age 年龄组和 breed 品种维度) | is_real: yes
- license: MIT | 活跃: unknown | star: HuggingFace 指标:Likes 2,Downloads last month 115,Followers 25(非 GitHub star) | 更新: insufficient data(页面未明确显示最后更新日期)
- 内容范围: 狗叫声(bark)音频数据集,用于狗年龄组分类(Audio Classification 任务)。总样本 22,808 条音频(1.01GB),训练集 17,888 条,测试集 4,920 条(公开 1,966 + 私有 2,954)。5 个年龄组:Adolescents/Senior/Adult/Juvenile/Puppy。7 类品种分布:Shiba Inu/Labrador/Chihuahua/Husky/German Shepherd/Pitbull/Other(Austrian Shepherd)。音频时长 0.06s-70.1s。训练集与测试集用户无重叠。模态 Audio,格式 soundfolder(自动转 Parquet)。属 Barkopedia 狗相关数据集系列。
- 备注: 核实结论:已知描述"约22.8k样本"与实际 22,808 rows 完全一致;"基于叫声的狗年龄组分类"与实际 Audio Classification 任务一致,描述属实无夸大。确为狗专属数据集(is_real_dog_kb=yes),但本质是音频分类训练数据而非"知识库/文档",属行为(叫声)领域数据集。MIT 许可,可公开使用。不作为对比报告重点候选:样本虽丰富但仅是单一分类任务的音频数据,无结构化知识/文档/本体,与"狗知识库"调研主题相关度中等。Barkopedia 为系列命名,本数据集为其中年龄组分类子集,系列内可能还有 breed/sex 等其他子集。无 BibTeX 引用信息

### Dog Knowledge Graph (pranjal-y4/Knowledge_Graph) 
- URL: https://github.com/pranjal-y4/Knowledge_Graph
- 类型: mixed | 子领域: ontology(横跨breed/disease-health/traits/care-food/training/lineage/general,以本体建模为核心) | is_real: yes
- license: 无(仓库未含LICENSE文件,repo页未声明许可证) | 活跃: stale(单日突发式3次上传,2026-02-18后无任何后续commit,0 star,无issue/PR活动迹象) | star: 0 | 更新: 2026-02-18(全部3次commit:Initial commit/Add files via upload/Update README.md,均同日由pranjal-y4提交)
- 内容范围: 确为犬类语义知识图谱,端到端语义数据管线。本体核心实体:Dog、Breed、Organization、Country、MedicalHealth、PhysicalTraits(下分Coat/Size(Small/Medium/Big)/Role)、Food、Training。关系/语义:object属性 hasBreed/ancestorOf/descendantOf(传递)/relatedBreed(对称)、datatype属性(函数约束);OWL逻辑约束(如每只狗有且仅一个breed)。技术栈:OWL本体+SHACL ingestion校验(基数/类型/必填)+RML映射(CSV→RDF,确定性IRI+join条件)+SPARQL查询(犬档案/按国家品种分析/谱系遍历/聚合/CONSTRUCT)+GraphDB三元组存储后端。LOD:通过owl:sameAs链接DBpedia与Wikidata。仓库文件:README.md、breeds.csv、dogs.csv、kg-dog.ttl(本体)、shacl.ttl、mapping.rml.ttl、interlinks.ttl、out.ttl、dkg.drawio.xml、chowlk-library-complete.xml、chowlk-library-lightweight.xml。无训练好的模型、无行为识别代码,纯语义建模。
- 备注: 已知描述与实际抓取内容高度一致,无夸大或矛盾:OWL+SHACL+RML+SPARQL栈、Dog/Breed/Health/Traits/Food/Training/Lineage建模、DBpedia/Wikidata via owl:sameAs均经README与repo文件清单证实。不作为对比报告重点的理由:0 star、单作者单日3 commit、无LICENSE、无持续维护、无社区影响力,属典型小规模学术/课程作业级KG,缺乏可作为权威参照的体量与活跃度。但若报告需要"犬类语义知识图谱"技术栈代表样本,本项目是精确匹配的最小实例,可在附录中提及。补注:GraphDB为后端但仓库不含部署

### mashequr/images_of_dog_breeds 
- URL: https://huggingface.co/datasets/mashequr/images_of_dog_breeds
- 类型: dataset | 子领域: breed | is_real: yes
- license: insufficient data (未指定) | 活跃: stale | star: 1 like | 更新: insufficient data (页面仅显示"last month"下载统计6次，无明确更新日期)
- 内容范围: 狗品种图像分类数据集。features: image(image dtype) + label(string, 21个类别)。splits: train(155 examples) + test(39 examples) = 194 总样本。download_size ~125.6MB, dataset_size ~127MB。数据格式 Parquet (data/train-*, data/test-*)。覆盖21个品种: Yorkshire Terrier, German Shepherd, Alaskan Malamute, Bulldog, Japanese Spitz, Rottweiler, Akita Inu, Labrador Retriever, Golden Retriever, Corgi, Poodle, German Shorthaired Pointer, Dachshund, Beagle, Pomeranian, Samoyed, Shiba Inu, Dobermann, French Bulldog, Sarabi dog, Jack Russell Terrier/Siberian Husky(疑似合并标签)。仅图像+标签，无行为/疾病/饲养/训练/本体等文本知识。
- 备注: 确为狗品种图像数据集，与已知描述(194样本)完全一致。README.md 仅含 YAML 元数据(dataset_info/configs)，无描述文本、无 license、无引用说明。数据集体量极小(194样本/21类，平均每类约9张)，活跃度低(1 like、月下载6次)，无维护信息。属于图像分类训练素材而非狗知识库/文档/本体。非对比报告重点候选。已知描述"约194样本"准确。无存疑点，抓取信息一致。

### StanfordExtra 
- URL: https://github.com/benjiebob/StanfordExtra
- 类型: dataset | 子领域: general(计算机视觉/动物姿态估计;非behavior/disease/breed/care/training/ontology,虽隐含120品种但标注本身为姿态关键点) | is_real: yes
- license: MIT(2024-11-02变更;版权属剑桥大学工程系Benjamin Biggs/Oliver Boyne/James Charles/Andrew Fitzgibbon/Roberto Cipolla,2020) | 活跃: stale | star: 113 | 更新: 2021-02-01(V12数据集,最近实质内容更新);2024-11-02仅License变更为MIT
- 内容范围: 约12,000张自然场景犬只(in-the-wild)图像的2D关键点(keypoints)+分割(segmentation)标注数据集。源自Stanford Dogs Dataset(ImageNetDogs,含120个品种)。附带demo.ipynb演示笔记本、关键点定义CSV、样本JSON、requirements。用于动物姿态估计与3D重建(配合WLDO/SMALify仓库)。提供train/validation splits及WLDO splits。标注通过Google form分发,图像来自Stanford Dogs Dataset。本质为计算机视觉标注数据,非行为/疾病/饲养/护理知识库。
- 备注: ECCV 2020论文《Who Left the Dogs Out? 3D Animal Reconstruction with Expectation Maximization in the Loop》(Biggs等)配套数据集。已知描述"12k张自然场景犬只2D关键点+分割标注数据集(ECCV 2020)"与实际完全一致,无营销夸大。确为狗专用数据集(源自Stanford Dogs Dataset, exclusively dogs)。55次commit,113 stars。两次抓取(GitHub主页+raw README)信息相互印证。注意:虽为狗数据集,但本质是CV姿态标注数据,非狗知

### benjamingray44/inertial-data-for-dog-behaviour-classification 
- URL: https://www.kaggle.com/datasets/benjamingray44/inertial-data-for-dog-behaviour-classification
- 类型: dataset | 子领域: behavior | is_real: yes
- license: 存疑冲突:数据集描述正文声明"CC BY 4.0"(Creative Commons Attribution 4.0 International,可分享/复制/修改),但页面 schema.org JSON-LD 元数据 license 字段标注为"CC BY-ND 4.0"(Attribution-NoDerivatives,禁止演绎)。两者不一致,以原始Mendeley源为准需进一步核验。 | 活跃: stale | star: 13 likes(Kaggle无star概念);下载742次;浏览6394次;评论0 | 更新: 2022-01-15(dateModified 2022-01-15T17:53:53Z,版本1,自2022年1月起无更新)
- 内容范围: 狗可穿戴惯性传感器(IMU)行为分类数据集。传感器:ActiGraph GT9X Link(3D加速度计+3D陀螺仪),采样率100Hz,放置于项圈与胸背带两处。行为标签7类:奔跑(galloping)、趴卧(lying on chest)、坐(sitting)、嗅闻(sniffing)、站立(standing)、快步走(trotting)、行走(walking)。文件:DogMoveData.csv(IMU xyz轴输出+行为标签)、DogInfo.csv(受试犬只信息)、Data_description.txt(列名说明)。数据规模约475MB(ZIP)。原始数据来自Mendeley(data.mendeley.com/datasets/vxhx934tbn/2),Kaggle为再上传镜像。有2篇同行评审论文支撑(Data in Brief 2022 数据描述;Applied Animal Behavior Science 241:105393, 2021 分类结果)。
- 备注: 抓取方式:Kaggle为JS渲染SPA,WebFetch仅得标题;改用mcp__fetch__fetch raw=true抓取HTML源码,从页面内嵌的schema.org Dataset JSON-LD元数据完整提取了描述/许可证/文件/统计/作者等全部关键字段,信息可信度高。

核实结论:
1. 确为真实狗行为数据集(is_real_dog_kb=yes),非图片分类器或通用动物数据集,明确针对犬只(canine),行为类别具体且专业。
2. 是原始数据集的Kaggle再上传镜像:上传者"Benjamin Gray"仅是搬运者,原始作者为Vehkaoja、Somppi、Törnqvist等

### Dog Behavior Location Dataset 
- URL: https://www.kaggle.com/datasets/kewinowens/dog-behavior-location-dataset
- 类型: dataset | 子领域: behavior | is_real: yes
- license: Unknown | 活跃: stale | star: 2 votes (Kaggle upvotes; not GitHub stars) | 更新: 2025-03-25
- 内容范围: 表格型观测数据,字段:Dog ID、Breed(如 Labrador/German Shepherd/Beagle)、Age、Weight(kg)、Latitude/Longitude(GPS 坐标)、Timestamp、Activity Level(低/中/高)、Behavioral Category(playful/aggressive/resting/exploring)、Weather Conditions(温度/湿度/风速/天气描述,来自 OpenWeatherMap API)、Noise Levels(dB)、Surrounding Environment(park/urban/rural/home)、Nearby Human Presence(10米半径人数)。用例:动物行为研究、宠物健康福祉、智能项圈跟踪、城市规划。注意:整体仅约136KB,疑为合成/示例数据而非大规模真实采集。
- 备注: Kaggle 主页为 SPA,WebFetch/fetch 仅得标题;改用 Kaggle 公开 API (https://www.kaggle.com/api/v1/datasets/view/<owner>/<slug>) 成功拿到完整 JSON 元数据。判定:确为狗相关数据集(is_real_dog_kb=yes),但属原始观测表格数据而非知识库/本体/文档。关键风险:数据体量仅136KB 与描述中"GPS trackers + behavioral observations + weather API 多源采集"严重不匹配,usability 评分仅0.294(29%),license 

### jthorvaldur/bulldogs (BulldogDerm / The Bulldog Dermatitis Handbook) 
- URL: https://github.com/jthorvaldur/bulldogs
- 类型: mixed | 子领域: disease (dermatology/skin health) | is_real: yes
- license: 未标注 (README与repo页均无license文件) | 活跃: active | star: 0 | 更新: 最近更新(repo页"last updated 11 minutes ago",约12 commits;README自动footer显示"10 commits"略滞后)。属新近活跃小项目。
- 内容范围: 斗牛犬皮肤健康(dermatology)循证知识库。覆盖:马拉色菌性皮炎(Malassezia dermatitis)、脱毛症(alopecia)等10种皮肤病症(分类:感染性/过敏性/内分泌性/寄生虫性/结构性);8个身体区域(面/耳/爪/腹/尾/躯干/腹股沟/后爪);治疗方案(外用/全身/社区验证/止痒管理);7步诊断流程;Cytopoint临床试验数据(Gober et al. 2022, n=62犬)。内容载体:20章手册(17页PDF)、5个Canvas2D交互可视化(病况网络图/身体地图/治疗流程图/诊断决策树/Cytopoint疗效图表)、结构化JSON数据(data/conditions.json)、18篇同行评审兽医皮肤科文献+社区参考(r/Bulldogs帖子,交叉核对)。明确声明非兽医建议,仅供教育。
- 备注: 抓取成功,repo主页与raw README双向印证一致。确为真实狗(斗牛犬)皮肤科循证知识库,描述与实际相符,无营销夸大,含兽医免责声明。类型实为mixed(文档+数据集+代码+部署静态站),非纯doc-kb。内容质量与结构化程度高(20章手册+10病况JSON+5可视化+18文献),但影响力极小(0 star,0 fork,约12 commits,单人jthorvaldur项目,且复用其morpheme-page/words_quantum_legal模板)。值得作为对比报告中的"小而精、垂直犬种+单病种循证KB"典型样本,但非高星主流项目。子域:疾病(皮肤科)。is_real_dog_k

### iDog 
- URL: https://ngdc.cncb.ac.cn/idog/
- 类型: mixed | 子领域: general(综合:品种/疾病/表型/行为/基因组/本体;横向覆盖多组学) | is_real: yes
- license: 数据库内容"仅限学术免费使用"(free for academic use only);2025 NAR论文开放获取 under CC BY-NC;代码托管于GitHub与FigShare | 活跃: active | star: insufficient data(数据库网站非GitHub repo,无star概念;代码仓库star未抓取到) | 更新: 2025-01(iDog 2.0发表于Nucleic Acids Research 2025 Vol.53 D1:D1039)
- 内容范围: 犬类多组学综合知识库,覆盖家犬(Canis lupus familiaris)与野生犬科动物(狼、豺)。数据维度:(1)基因组-4个参考基因组(CanFam3.1/CanFam4),CanFam4含30,653基因;(2)变异-1,929现代样本29.5M SNPs+16.5M InDels、111古代样本29M SNPs、145品种43,487品种特异SNPs、530疾病关联变异;(3)转录组-141 BioProjects/84组织/2,947实验、28,145差异表达基因(31种疾病);(4)单细胞-Beagle海马105,057细胞26簇;(5)表观组-547 DNA甲基化样本、87 ATAC-seq样本;(6)表型-897犬病、3,207 G2P对、349疾病基因、482标准品种、8,309疾病文献;(7)本体-Dog Breed Ontology 456词条、Dog Disease Trait Ontology 1,536词条;(8)工具13个-AI检索DogRAG、品种图像分类DogVC(94.5%准确率)、Fst/Pi/Tajima's D、GO/KEGG富集等;(9)表型子模块含Dog Breed/Dog Disease/G2P/Dog-Human Disease。涉及行为模式、驯化、形态发育、人类遗传病模型。
- 备注: 核实结论:确为真实犬类知识库,描述与实际一致,无营销夸大。核实过程:(1)WebFetch抓主页https://ngdc.cncb.ac.cn/idog/确认其为Vue SPA,正文仅`<div id="app"></div>`空壳,JS渲染内容未抓到(与已知描述吻合);(2)抓JS bundle确认仅含Vue框架代码,无业务文本;(3)Google搜索被反爬拦截;(4)改用DuckDuckGo HTML搜索成功,获得9条结果标题与摘要,确认iDog为NGDC/CNCB/BIG/CAS开发的犬类综合资源;(5)抓2025 NAR论文页academic.oup.com/nar/article/5

### 729r2pzfqs-ux/breed-guide (BreedFinder) 
- URL: https://github.com/729r2pzfqs-ux/breed-guide
- 类型: mixed (结构化数据集 data/breeds.json + 静态知识库网站 HTML + Python 工具脚本;本质为 dog breed 知识库/数据集) | 子领域: breed(主);部分覆盖 behavior(temperament 气质标签)、disease/health(每品种 health 字段含特异疾病)、care(grooming/exercise)、training(trainability 评分)、general(articles/FAQ) | is_real: yes
- license: insufficient data(仓库主页未注明;repo 根目录未见 LICENSE 文件) | 活跃: unknown(672 次提交提示有开发活动,但 0 star/0 fork/0 watcher 且无法核实最后提交日期,无法判定 active/stale) | star: 0 | 更新: insufficient data(仓库主页显示 672 commits 但未暴露具体日期;GitHub API 无 token 返回 403,gh CLI 不可用,atom 订阅被 robots.txt 禁止,无法精确获取最后提交日期)
- 内容范围: 犬品种知识库。核心为 data/breeds.json 结构化数据集,覆盖 220+ 犬品种,每品种含:id、多语别名(aliases)、group(akc 分组)、origin 国家、lifespan、size(身高/体重/体型类别)、8 维 ratings(size/energy/grooming/sociability/trainability/barking/kid_friendly/apartment_ok 各 1-5 分)、characteristics(毛质 coat_type/毛色 coat_colors/掉毛 shedding/低敏 hypoallergenic)、temperament 气质标签数组、description(overview/history/temperament/health/grooming/exercise 编辑撰稿,health 字段含品种特异疾病如髌骨脱位/髋关节发育不良/心脏杂音)、verdict(best_for/not_for/summary 裁决)、tagline。网站另含:~3000 个品种两两对比页、品种匹配 quiz、6 篇生活方式文章(公寓/家庭/老人/低敏/低掉毛/低维护)、FAQ、搜索、品种索引。16 语言本地化(da/de/es/fi/fr/it/ja/nl/no/pl/pt/ru/sv/tr/zh + en),共 6600+ 页面。含 SEO 结构化数据(JSON-LD/FAQ schema)与 llms.txt。
- 备注: 核实结论:确为真实狗知识库/数据集,描述与实际一致,无营销夸大,无信息矛盾。核心证据为 data/breeds.json —— 220+ 品种的结构化编辑数据,字段丰富(评分/特征/气质/健康含疾病/美容/运动/裁决),是真知识库而非图片分类器或同名无关项目。该项目实为 breedfinder.org 静态站的源码镜像,以 GitHub Pages 托管(CNAME 指向 breedfinder.org),Python 脚本用于多语翻译与 FAQ schema 生成。信息缺口:(1) 仓库无 README.md(HEAD/main 均返回 404/429,以 llms.txt 替代核实内容);

### Dog Emotion Dataset (Cleaned Version) 
- URL: https://www.kaggle.com/datasets/mohitagarwal17/dog-emotion-datasetcleaned-version
- 类型: dataset | 子领域: behavior | is_real: yes
- license: Apache 2.0 | 活跃: active | star: 7 votes / 79 downloads / 549 views (Kaggle无star机制,以vote计) | 更新: 2026-06-20 (v3,初始版2026-06-17)
- 内容范围: 狗情绪图像分类数据集,4个情绪类别:Angry(愤怒)/Happy(高兴)/Relaxed(放松)/Sad(悲伤)。混合多源公开狗情绪数据集并人工清洗,去除模糊/重复/错标样本,各类别平衡。总大小约145MB(原始未清洗版160MB)。用途:狗情绪识别、图像分类、迁移学习、计算机视觉研究、预训练模型(ConvNeXt/EfficientNet/ResNet)基准测试。兼容PyTorch/FastAI/TensorFlow。注意:这是图像数据集(像素数据+标签),非结构化知识库/文档/本体。
- 备注: 通过Kaggle公开API(/api/v1/datasets/view/)成功获取完整元数据,WebFetch与原始HTML抓取均因Kaggle纯JS渲染只返回标题,API为可靠佐证来源。确为专门关于狗的数据集(标签含animals,标题/描述均明确dog),内容为狗情绪4分类图像,属行为/情绪领域。判断is_real_dog_kb=yes(确为狗数据集),但需注意它是图像分类训练数据而非知识库/文档/本体——若对比报告聚焦"狗知识库/结构化知识",此项目仅作为"图像型狗情绪数据"的对照参考。非重点候选原因:体量小(145MB)、发布新(2026-06-17首发,距今约半个月)、关注度低(7票

### subihwang/dogbarkdatasound 
- URL: https://www.kaggle.com/datasets/subihwang/dogbarkdatasound
- 类型: dataset | 子领域: behavior | is_real: yes
- license: Apache 2.0 | 活跃: stale | star: 0 (Kaggle 点赞数=0;浏览334/下载15/评论0) | 更新: 2023-10-29 (dateModified: 2023-10-29T08:38:34.883Z,仅 1 个版本,此后无更新)
- 内容范围: 狗吠叫音频数据集,zip 压缩,约 260MB(260,712,672 bytes),仅 1 个版本。描述为 Kaggle 模板文字("# Dataset / This dataset was created by subihwang / Released under Apache 2.0 / # Contents"),# Contents 之下无任何实际内容说明,无关键词。无品种/录音条件/样本数/音频格式/行为上下文等元数据。使用 Kaggle 默认缩略图(未自定义预览)。需登录 Kaggle 才能下载。外部搜索无论文引用、无 GitHub 仓库使用、无 notebook 示例。仅发现不相关的同类数据集(arXiv:2404.18739 用的是别的数据集;Barkopedia/DogSpeak/AudioSet bark 均为独立数据集)。
- 备注: 真实抓取结果:Kaggle 页面为 JS 渲染,首次 WebFetch 仅得标题;改用 raw HTML fetch 成功获取 Kaggle 官方嵌入的 JSON-LD(schema.org Dataset)权威元数据,据此确认事实。确为狗相关数据集(狗吠叫音频),故 is_real_dog_kb=yes,但需注意:它只是 260MB 原始音频 zip 包,非知识库/文档,描述极简陋(模板文字、# Contents 下空白)、无关键词、无品种/样本数/录音条件等元数据、用默认缩略图。互动极低(334浏览/15下载/0评论/0点赞)、仅 1 版本、2023-10 后无更新,处于 stale 状态

### 120 Dog breeds Images for Classification (vikaschauhan734) 
- URL: https://www.kaggle.com/datasets/vikaschauhan734/120-dog-breed-image-classification
- 类型: dataset | 子领域: breed | is_real: yes
- license: Unknown(未指定,Kaggle schema 标注 license name="Unknown" url 为空) | 活跃: stale | star: N/A(Kaggle 无 star 概念;互动数据:点赞1 / 下载505 / 浏览2125 / 评论0) | 更新: 2023-05-26(dateModified)
- 内容范围: 狗品种图像分类数据集。120个文件夹对应120个独特狗品种,文件夹名即品种名;共20,580张已标注图像,776MB zip包,免费可下载。专为狗品种分类(图像识别/计算机视觉/深度学习)任务设计,用于训练和评估品种识别模型。仅含品种视觉图像标签,不涉及行为/疾病/饲养/训练/本体等知识。
- 备注: Kaggle 数据集(非 GitHub repo),通过页面 JSON-LD 结构化数据(schema.org Dataset)获得权威元数据,描述与实际内容一致无夸大。确为狗相关数据集,但仅是品种图像分类素材,非知识库/文档/本体;含品种标签但无行为、疾病、饲养、训练等知识维度。活跃度低:1赞/505下载/0评论,版本1自2023-05-26起未更新(距今3年+),776MB。creator=Vikas Chauhan, isAccessibleForFree=true。已知描述"20580张图/120品种"经核实属实。不适合作为对比报告重点(同类品种图像数据集众多且本数据集体量小、活跃度低

### Dog Breed Identification (Kaggle) 
- URL: https://www.kaggle.com/c/dog-breed-identification
- 类型: dataset | 子领域: breed | is_real: yes
- license: Kaggle竞赛规则约束(非标准开源许可),具体条款insufficient data | 活跃: archived | star: N/A(Kaggle无star概念;以竞赛队伍数/leaderboard衡量) | 更新: 2017(竞赛举办年,已结束;数据集持续可下载,具体维护日期insufficient data)
- 内容范围: 狗品种识别图像数据集(Kaggle竞赛)。120个犬种细粒度分类,训练集10,222张+测试集10,357张JPEG/RGB图像,评估指标Multi-Class Log Loss。基于Stanford Dogs Dataset(ImageNet子集,Aditya Khosla/Nityananda Jayadevaprakash/Bangpeng Yao/Fei-Fei Li构建)。官方描述:"Determine the breed of a dog in an image"。内容仅覆盖品种外观识别,不含行为/疾病/饲养/训练/本体等维度。
- 备注: 抓取限制:Kaggle全站JS渲染,WebFetch/mcp__fetch直接抓取与Wayback常规快照均仅返回页面title与空body。改用Wayback的id_原始内容前缀抓到HTML头部,确认官方meta description="Determine the breed of a dog in an image"、og:url=https://kaggle.com/dog-breed-identification、竞赛ID=7327、类目=Competitions,证实项目真实且为犬专属。具体数字(120品种/10222+10357图/Multi-Class Log Loss/Sta

### Meta-Album DOG (Dogs Dataset) 
- URL: https://meta-album.github.io/datasets/DOG.html
- 类型: dataset | 子领域: breed | is_real: yes
- license: Meta-Album 发布版: CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/);原始数据: "Cite to use dataset, open for research" | 活跃: stale | star: insufficient data (非 GitHub repo,为数据集主页,无 star 概念) | 更新: 2022-12-15 (页面 Last updated;Created 2022-03-01)
- 内容范围: 犬类品种细粒度图像分类数据集:120 个犬品种,共 20480 张 128x128 px 图像(预处理自 Stanford Dogs/ImageNet 原图,裁剪为正方形并抗锯齿缩放)。每类 148-252 张,类间差异小、类内差异大(颜色/姿态/遮挡)。仅覆盖品种识别,不含行为/疾病/饲养/训练/本体等文本或结构化知识。提供 Micro/Mini/Extended 三个版本(OpenML ID 44313/44298/44331)。
- 备注: 确为真实犬类数据集,属 Meta-Album 多领域元数据集(NeurIPS 2022 Datasets & Benchmarks Track)的 Large Animals 域子集,Meta Album ID: LR_AM.DOG。原始作者 Aditya Khosla 等(Stanford),Meta-Album 整理者 Dustin Carrion,联系人 Ihsan Ullah (meta-album@chalearn.org)。本质是图像分类数据集,非文本/结构化"知识库",无品种描述文本、医学或行为知识。已知描述与实际页面完全一致(120 品种/20480 张/128x128/Mic

### AtharvaTaras/Dog-Breeds-Dataset 
- URL: https://github.com/AtharvaTaras/Dog-Breeds-Dataset
- 类型: dataset | 子领域: breed | is_real: yes
- license: CC-BY-4.0 | 活跃: stale | star: 11 | 更新: 2023-02-02 (最后提交为 Update README.md,SHA 7164ba6)
- 内容范围: FCI(Fédération Cynologique Internationale)认可犬种的纯图像数据集。共 356 个品种,每品种 35 张图片,未压缩约 5.32GB,README 自述约 2-7% 重复图片。品种按文件夹组织(如 affenpinscher dog、beagle dog、chow chow dog)。仅含 README,无代码、无知识文本。不含行为/疾病/饲养/训练等知识维度,仅用于品种图像分类/识别。
- 备注: 抓取双源一致(WebFetch repo 主页 + mcp__fetch__fetch 原始 README + commits 页),描述与实际相符无夸大。该项目为 scraper 批量抓取的品种图像素材,33 个提交集中在 2023-02-01 当天,2023-02-02 后无更新,截至 2026-07 已停滞 3 年多。确为狗相关数据集但仅限品种图像,非狗知识库/文本知识,且规模小(11 stars)、有重复图片质量问题,不适合作为狗知识库对比报告重点。已知描述"FCI 认可犬种的图像数据集"准确。

### consigcody94/calm-hound (Calm Hound) 
- URL: https://github.com/consigcody94/calm-hound
- 类型: doc-kb | 子领域: behavior/training (狗分离焦虑 separation anxiety) | is_real: yes
- license: 未标注(not specified,无 LICENSE 文件,页面无版权声明) | 活跃: stale/unknown(单次提交、0 star、0 fork、无 release) | star: 0 | 更新: insufficient data(仓库仅 1 次 commit,页面未显示日期;GitHub API 抓取返回 403 无法取 pushed_at)
- 内容范围: 静态 HTML 内容站,聚焦狗分离焦虑(separation anxiety)的正向(force-free)引导。仓库含 articles/ 目录,内 3 篇免费文章:dog-separation-anxiety-what-to-do-tonight.html(今晚该怎么做)、how-long-can-dog-with-separation-anxiety-be-alone.html(能独处多久)、punishing-dog-separation-anxiety.html(为何惩罚适得其反),加 index.html。线上站(consigcody94.github.io/calm-hound/)另售付费电子书 The Calm Dog Protocol($19,Gumroad,14天计划+The First 72 Hours危机指南+14天进度日志,30天退款)。主题:脱敏训练、独处恐惧、药物与行为训练配合、惩罚为何加重恐惧。
- 备注: 核实结论:确为狗相关文档站,聚焦分离焦虑正向训练,已知描述(含 articles 目录、托管于 GitHub Pages)属实。但需对抗性提示——(1)仓库极薄:单次提交、3 篇免费 HTML 文章、0 star,更像个人内容/营销落地页而非结构化知识库/数据集;(2)免费指南背后藏着 $19 付费电子书 The Calm Dog Protocol(Gumroad 售卖),已知描述的"免费正向引导指南"只覆盖仓库内的免费部分,商业转化未提及;(3)无 README(HEAD/main 均返回 404)、无 LICENSE、无作者署名、无提交日期元数据(API 403)。作为对比报告重点价值低:

### Dog Behavior Monitoring Dataset (ziya07) 
- URL: https://www.kaggle.com/datasets/ziya07/dog-behavior-monitoring-dataset
- 类型: dataset | 子领域: behavior | is_real: yes
- license: CC0: Public Domain | 活跃: stale | star: Kaggle无star系统;2 votes / 211 downloads / 2168 views / 0 kernels / 0 topics;usability 0.71 | 更新: 2025-04-25 (v1 Initial release,此后无更新)
- 内容范围: 狗行为监测数据集,主题为分离焦虑(separation anxiety)早期检测。三级行为层级:Level1基础姿态(颈部/背部三轴加速度:Bark/Walk/Sit/Stand/Lie/Dig/Jump,头部姿态Bark/HeadDown/HeadUp);Level2原子行为(Sniffing/Walking/Lying/Sitting/Standing/Digging/Barking/Escaping/Idle);Level3复杂行为(基于模糊逻辑:Excessive Vocalization/Destructive/Exploratory,15秒窗口判定Normal/Abnormal)。列:dog_id,timestamp,neck_x/y/z,back_x/y/z,head_posture,body_posture,atomic_behavior,complex_behavior。关键限制:数据为模拟/合成(simulated),仅1只狗(Dog_01),60秒时长,50Hz采样约3000条,姿态为"随机选取"后规则推导标签,非真实观测数据。
- 备注: 通过Kaggle公开API(/api/v1/datasets/view/)获取完整JSON元数据成功;Kaggle网页为JS渲染,WebFetch仅得到标题,改用API拿到全部字段(description/license/counts/versions)。

核验要点(需对抗核验):
1. 主题确为狗行为监测(separation anxiety/姿态/原子行为/复杂行为),is_real_dog_kb=yes;但数据为SIMULATED合成数据,非真实狗观测——head_posture/body_posture"selected randomly",原子行为由规则推导,复杂行为由模糊逻辑15

### iDog Processing Pipelines (Br1anChou/idog) 
- URL: https://github.com/Br1anChou/idog
- 类型: mixed | 子领域: general(犬科多组学/基因组学,覆盖品种/疾病/行为/形态/驯化) | is_real: yes
- license: MIT | 活跃: unknown | star: 4 | 更新: insufficient data(主页显示 44 commits,未暴露具体最后提交日期;关联论文为 2024 NAR)
- 内容范围: iDog2.0 数据处理流水线 + Dog10K 联盟数据门户。包含 bulkRNA-seq(STAR/RSEM/kallisto)、ATAC-seq(bowtie2/macs2)、WGBS/BS-seq(bismark) 三类生物信息流水线脚本;reference/UU_Cfam_GSD_1.0/ 含 CanFam4 参考基因组文件;Tools/ 工具集。覆盖犬科多组学:基因组、转录组、表观基因组、表型组、单细胞转录组,样本跨度从古代到现代犬、多品种、不同年龄与组织,支持驯化/性状/行为/形态/疾病易感性研究。仓库结构:ATAC/、bulkRNA/、WGBS/、Tools/、reference/、LICENSE、README.md。
- 备注: 两次抓取(GitHub 主页 + raw README)信息一致,描述与实际相符,无营销夸大。确为犬科(canid)基因组学真实学术资源:iDog 2.0 是国际 Dog10K 项目与联盟的官方数据门户,基于 CanFam4 参考基因组,关联 2024 NAR 论文(DOI:10.1093/nar/gkae1031,Yanhu Liu et al., "iDog: a multi-omics resource for canids study")。注意:本仓库是"数据处理流水线代码+参考基因组文件",非传统知识库/文档,但其上游 iDog 门户含多组学数据(基因组/转录组/表观/表型/单细胞)

### DogSpeak (DogSpeak_Dataset) 
- URL: https://huggingface.co/datasets/ArlingtonCL2/DogSpeak_Dataset
- 类型: dataset | 子领域: behavior (vocalization / bioacoustics 吠叫发声) + breed classification | is_real: yes
- license: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International) | 活跃: active (月下载 16 万+,有 2025 同行评审论文背书) | star: 7 likes / 25 followers / 162,481 downloads last month (HuggingFace 用 likes 非 GitHub stars) | 更新: README 关联 2025 ACM MM 论文(Lekhak, Wang, Dang, Zhu — Proceedings of the 33rd ACM International Conference on Multimedia, pp.13369-13375, 2025);数据集页未显式标注最后更新日期
- 内容范围: 大规模野外犬类发声(吠叫/bark sequence)分类数据集。含 77,202 段 Bark 序列,来自 156 只犬、5 个品种(吉娃娃 Chihuahua / 德牧 German Shepherd / 哈士奇 Husky / 比特 Pitbull / 柴犬 Shiba Inu)。每段附标签:breed(品种)、sex(性别 male/female)、dog_id(犬唯一标识)、filename。WAV 音频文件,按 dog_id 目录组织,附 metadata.csv。总大小 3.83GB。用途:品种分类、性别分类、犬类发声建模、音频表征学习、生物声学基础模型预训练、大规模犬类声学分析。覆盖 subdomain:行为(vocalization/生物声学)+ 品种分类。
- 备注: 核实结论:数据集真实存在,描述与 README 高度吻合(77,202 段 / 156 只犬 / 5 品种 / breed+sex+dog_id 标签 / 3.83GB / CC BY-NC-SA 4.0 全部一致)。\n\n存疑点(uncertainty=true 原因):已知描述中的"33.16 小时"总时长在 README 与数据集卡中均未出现 — README 只对相关的 CATVD(Canine Age Transition Vocalization Dataset)数据集提到约 11.4 小时,DogSpeak 自身总时长未在卡片标注。33.16 小时可能源自 ACM 论文正文或其

### mashequr/dog_breed_images 
- URL: https://huggingface.co/datasets/mashequr/dog_breed_images
- 类型: dataset | 子领域: breed | is_real: yes
- license: 未标注(Not specified) | 活跃: stale | star: 0 likes(HF无star概念,likes=0) | 更新: 2024-07-28(lastModified,createdAt同为2024-07-28)
- 内容范围: 狗品种图像分类数据集。181张狗品种图像(244px宽),21个品种类别:French Bulldog, Poodle, Alaskan Malamute, Shiba Inu, Rottweiler, Golden Retriever, Beagle, German Shepherd, Pomeranian, Dobermann, Labrador Retriever, Corgi, Japanese Spitz, Dachshund, Akita Inu, Samoyed, Bulldog, Yorkshire Terrier, Sarabi dog, German Shorthaired Pointer, Jack Russell Terrier/Siberian Husky。结构:train(144样本)/test(37样本),Parquet格式,总大小约103MB。特征:image(image dtype)+label(string)。仅用于品种识别/分类,无行为/疾病/饲养/训练等知识内容。
- 备注: 三次抓取一致(WebFetch页面/mcp__fetch__fetch页面/HF API)。确为真实狗品种图像数据集,已知描述"狗品种图像数据集,约181样本"与实际完全吻合,无夸大或矛盾。但价值有限:1)体量极小(仅181样本,21类);2)无任何文档/说明,dataset card仅写"More Information needed";3)无license;4)活跃度极低(0 likes,月下载8次,2年未更新);5)是图像分类数据集而非结构化狗知识库,不含行为/疾病/饲养/训练/品种百科等知识内容。不建议作为对比报告重点,仅可作为"小规模图像分类数据集"的边缘样本提及。HF API元数据

### tom-sims/ManyDogs-Project-Analysis-of-Pet-Dog-Behaviour-and-C-BARQ-Scores 
- URL: https://github.com/tom-sims/ManyDogs-Project-Analysis-of-Pet-Dog-Behaviour-and-C-BARQ-Scores
- 类型: mixed | 子领域: behavior | is_real: yes
- license: 未列出(无 License) | 活跃: stale | star: 1 | 更新: insufficient data(主分支仅 2 次 commit,页面上无明确日期)
- 内容范围: 使用 R 对 ManyDogs 数据集做宠物狗行为分析:汇总狗的特征、计算 C-BARQ(Canine Behavioral Assessment & Research Questionnaire,标准化犬类行为评估问卷)总行为评分、可视化分布、探索行为评分与年龄/性别的关系。仓库根目录含 4 个文件:manydogs_data.csv(数据集)、Projectcode.R(R 分析脚本)、Many Dogs Poster.pdf(一页结果海报)、README.md。覆盖维度为 behavior(行为评分统计与可视化),不涉及疾病/品种/饲养/训练/本体。
- 备注: 真实抓取 GitHub 主页 + raw README 双源核实,信息一致,描述与实际相符(非营销夸大)。确为狗行为知识相关数据集+代码项目,但规模极小:1 star、2 commits、根目录仅 4 个文件(1 个 CSV + 1 个 R 脚本 + 1 张海报 PDF + README),无 License,无明确更新日期。C-BARQ 是国际通用的标准化犬类行为评估问卷,数据本身有科学价值,但此仓库仅为一份小型课程/个人练习级分析,非系统化知识库/文档库,不建议作为对比报告重点。如需 ManyDogs 原始数据,应追溯 ManyDogs Project 上游官网而非此衍生分析仓库。

### Stanford Dogs Dataset 
- URL: http://vision.stanford.edu/aditya86/ImageNetDogs/main.html
- 类型: dataset | 子领域: breed | is_real: yes
- license: insufficient data (页面与README均未声明许可证,仅要求引用CVPR 2011论文) | 活跃: archived | star: insufficient data (非GitHub仓库,为斯坦福视觉实验室静态网页,无star概念) | 更新: insufficient data (页面无更新日期;数据集首发于CVPR 2011 FGVC workshop,属静态归档数据集)
- 内容范围: 120个犬种、20,580张图片的细粒度图像分类基准数据集。标注含类别标签(class labels)与边界框(bounding boxes)。源自ImageNet图像与标注。文件结构:images/(按品种分文件夹)、annotations/(边界框)、file_list.mat、train_list.mat、test_list.mat、train/test特征矩阵(直方图交叉核)。提供train/test划分。仅含视觉品种分类数据,无行为/疾病/护理/训练/本体等结构化知识。
- 备注: 抓取成功(主页面+README.txt均获取)。确为狗专属数据集:120品种20580张图片,含类别标签与边界框标注,源自ImageNet,与已知描述完全吻合无偏差,无需对抗核验。经典学术基准(CVPR 2011,作者Aditya Khosla/Li Fei-Fei等,斯坦福大学),广泛被细粒度图像分类领域引用。但本质是图像分类数据集而非结构化知识库:仅含视觉品种分类数据,无行为/疾病/护理/训练/本体知识。作为对比报告重点的定位:典型代表性强(狗品种图像分类的canonical基准),但若报告聚焦"知识库/结构化知识"则其相关性偏弱,仅为图像数据。未声明许可证、无star/活跃度指标(静态归

### DucNgn/Dog-Facts-API-v2 
- URL: https://github.com/DucNgn/Dog-Facts-API-v2
- 类型: mixed | 子领域: general | is_real: yes
- license: MIT | 活跃: stale | star: 5 | 更新: insufficient data (commits 页被 robots.txt 禁止抓取,GitHub API 无 token 返回 403;repo 显示共 9 commits)
- 内容范围: 根目录 data.json 含 56+ 条(截断,完整约 100+ 条)狗事实文本字符串。主题覆盖:品种(Chihuahua/Basenji/Dachshund/Newfoundland/Bloodhound/Dalmatian/Border Collie 等)、行为(摇尾、便后刨地标记、吠叫最多品种、服务犬工作状态)、解剖感官(嗅觉 220M 细胞、耳肌、第三眼睑/nictitating membrane、心率 120/分、鼻腔湿润定向)、历史演化(狼后裔、Tomarctus、古埃及/古希腊/古中国驯化、10,000 B.C. 化石)、饲养护理(8-12 周领养最佳、幼犬出生盲聋、小型犬寿命更长)、健康相关(巧克力 theobromine 中毒、癫痫预警训练、Search and Rescue 嗅人)。无系统化疾病/训练/本体论条目,事实零散偏百科冷知识。
- 备注: 确为真实狗事实知识库 + API,但体量小(5 star / 9 commits / 约百条事实)、是 kinduff/dog-api 的 Python/FastAPI 端口移植,非原创数据。事实为通用冷知识型百科,覆盖品种/行为/解剖/历史/饲养/健康但每条零散、无结构化字段(仅 fact 字符串)。作对比报告可作次要参考(实际可用的狗事实 API 实例),但非重点;上游原创 kinduff/dog-api 更具代表性。README 未列 license,license 来自 repo 元数据页。部署地址 www.dogfactsapi.ducnguyen.dev。

### Deep-Learning-Fine-Grained-Action-Recognition-Canine-Behavior (samtwl) 
- URL: https://github.com/samtwl/Deep-Learning-Fine-Grained-Action-Recognition-Canine-Behavior
- 类型: mixed | 子领域: behavior | is_real: yes
- license: No license specified | 活跃: stale | star: 2 | 更新: insufficient data (repo 显示 13 commits,无明确日期)
- 内容范围: 犬类细粒度行为动作识别研究项目。code/ 含 11 个 Jupyter notebook:3SCNN+LSTM、frame_extracting、incept(global/local) 多种组合(含+LSTM+avg)、simple(global/local) 多种组合,覆盖 CNN+LSTM 双流架构与光流变体;paper/ 含实际 PDF 论文 "Deep-Learning-Fine-Grained-Action-Recognition-Canine-Behavior.pdf";data/ 仅有 Permission-to-Use-Data.md,数据集不公开,需申请(request upon request)。README 仅两行说明。主题标签:action-recognition, video-classification, fine-grained-classification, computer-vision, optical-flow, cnn, lstm, keras-tensorflow。
- 备注: 项目真实,确为犬类(canine)细粒度行为识别,与已知描述基本吻合。核实要点:(1) code/ 确有 11 个 notebook,方法标签含 cnn/lstm/optical-flow,与"CNN+LSTM+光流,捕捉时空上下文"描述一致;(2) paper/ 确有 PDF 论文,与"含论文"一致;(3) 数据集不公开——已知描述"含数据集"易让人以为可下载,但 data/ 目录只有 Permission-to-Use-Data.md 许可说明,README 明确写 "dataset will be available upon request",实际数据需向作者申请,此点描述与实际有出入

### Dog10K 
- URL: https://dog10k.kiz.ac.cn/
- 类型: dataset | 子领域: breed | is_real: yes
- license: insufficient data (首页未标注许可;数据下载页未抓取到许可条款) | 活跃: active | star: N/A (非 GitHub 仓库,为中科院昆明动物所托管网站数据库,无 star 概念) | 更新: 2024-10-22 发表于 Nucleic Acids Research (DOI:10.1093/nar/gkae928);首页版权 Copyright © 2024 昆明动物所。网站当前可访问,具体数据更新时间未在首页标注。
- 内容范围: 国际犬类基因组多组学协作数据库( Dog10K project),NAR 2024 发表。核心数据: (1)SNVs 52,963,969 个(约5296万),来自 1987 个犬科个体(324 品种/类群:1611 家犬+309 村犬来自26国+63 狼+4 郊狼);(2)DNMs 新生突变 8565 个,来自 643 狗/404 三人组/54 多代家系/43 品种;(3)单细胞 RNA:海马体 105,057 单核(5月龄比格犬,SPLiT-seq,8细胞类型)+白细胞 74,067 细胞(17狗含10骨肉瘤+7健康,46簇);(4)衰老转录组:30 狗(1-9岁)+469 人(8-73岁,来自GSA/NGDC),718 基因年龄相关表达模式 Pearson>0.8;(5)4 基因组组装(canFam3-6);(6)分析工具:Genome Browser/LiftOver 坐标转换/Selscan 选择分析/AgeConversion 年龄换算;(7)下载分 Omics 与 Behavior 两类。覆盖品种/遗传/疾病(骨肉瘤)/衰老/行为多维度。
- 备注: 核实结论: 已知描述与 NAR 2024 权威论文完全吻合(1987个体/324品种/5296万SNV/8565DNMs/单细胞+衰老转录组/三大工具均逐一坐实)。首页与论文的数字差异已解释: 首页显示 8,312 DNMs 与 2,075 个体为高质量/QC 子集,论文 8,565 DNMs 与 1,987 个体为总数(QC 通过阈值);均为同一数据集不同口径,非矛盾。首页还提及 Behavior 下载(行为数据)与疾病维度(骨肉瘤 scRNA),实际覆盖比已知描述更广。托管方: 中国科学院昆明动物所(Kunming Institute of Zoology, CAS),滇ICP备05000

### ArlingtonCL2/Barkopedia_Individual_Dog_Recognition_Dataset 
- URL: https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Individual_Dog_Recognition_Dataset
- 类型: dataset | 子领域: behavior/vocalization (bark audio), individual dog identification | is_real: yes
- license: MIT | 活跃: stale | star: 0 (HF likes) | 更新: insufficient data (页面未显式标注更新日期)
- 内容范围: 狗叫声(bark)音频数据集,共8,924条标注音频,用于个体狗识别(60个狗个体ID,编号1-60)。训练集7,137条(~120条/狗),测试集1,787条(~30条/狗,其中709条公开榜单+1,078条私有终评)。音频时长0-70.4秒,总433MB,soundfolder格式。标签文件train_labels.csv含audio_id与pred_dog_id两列。任务为Audio Classification,标签人工生成并验证。无品种/疾病/护理等知识,仅个体级别识别。
- 备注: 抓取成功,WebFetch 与 mcp__fetch__fetch 两次结果完全一致,描述与实际相符(8.92k样本确认)。确为狗专属数据集(狗叫声音频,MIT许可)。但本质是音频生物声学/机器学习训练数据(Audio Classification),非结构化狗知识库(无品种/疾病/护理/行为事实知识)。发布方:Arlington Computational Linguistic Lab (ArlingtonCL2)。挑战官网 uta-acl2.github.io/barkopedia.html 已404(项目可能已归档)。HF点赞0,月下载57,活跃度低。适合作为"狗相关数据集"对比的边缘案

### Stanford-Dogs-OWL-Ontology 
- URL: https://github.com/miranthajayatilake/Stanford-Dogs-OWL-Ontology
- 类型: doc-kb | 子领域: breed/ontology | is_real: yes
- license: 无 (repo 未声明任何 license) | 活跃: stale | star: 1 | 更新: 2021-02 (本体 IRI 标注 mirantha/ontologies/2021/2;repo 仅 1 次 commit,此后无更新)
- 内容范围: 基于 Stanford Dogs 数据集构建的狗品种分类本体(OWL)。包含两个文件:dogs_dataset_ontology.owl(完整版)与 dogs_dataset_ontology_reduced.owl(精简版)。本体使用 WordNet 同步集命名(如 affenpinscher.n.01、afghan_hound.n.01、golden_retriever.n.01 等),涵盖约 120 个狗品种,并附带分类层级上位词(animal.n.01/carnivore.n.01/canine.n.02/dog.n.01/mammal.n.01/chordate.n.01/living_thing.n.01/entity.n.01/object.n.01)。仅覆盖品种分类学(taxonomy),不涉及行为、疾病、饲养、训练等内容。无 README、无文档、无示例代码、无 license。
- 备注: 核实结论:确为狗知识库/本体,与已知描述一致,无营销夸大。抓取三处佐证:(1) GitHub repo 主页 → 1 star / 1 commit / 无 license / 无 README / 无 description;(2) raw README 在 HEAD 与 master 分支均 404,证实确实无 README 文件;(3) raw OWL 文件成功获取,内容为狗品种分类本体(120 个品种类 + WordNet 上位层级),创建于 2021 年 2 月。判断要点:is_real_dog_kb=yes(确为狗品种本体),但范围极窄(仅品种分类学,无行为/疾病/饲养/训练),内

### Dog Breed Ontology (Tetherless-World / RPI OE2022) 
- URL: https://tetherless-world.github.io/ontology-engineering/oe2022/dog-breed-ontology/related_work.html
- 类型: mixed | 子领域: breed / ontology (品种特征建模与推荐,非行为/疾病/饲养) | is_real: yes
- license: MIT License (页面 license.html 声明 "Copyright © 2022 DogBreedOntologies Team";但仓库根目录无 LICENSE 文件) | 活跃: stale | star: 13 (注:为整个 ontology-engineering 课程仓库的 star,dog-breed-ontology 为其子目录,无独立 star) | 更新: 约 2022-11 (Fall 2022 课程项目, VBO 评估 "as of Nov. 2022";子项目此后静态未更新。父仓库共 2496 commits 持续维护至 2024+ 含 oe2024/oe2026)
- 内容范围: 犬品种语义本体(RDF/OWL),建模品种特征:低敏(hypoallergenic)、公寓友好、吠叫级别(barking)、陌生人友好、犬只友好、体型(extra small~extra large)、脱毛(shedding)、流涎(drooling)、儿童友好、玩耍/亲昵、可训练性(trainability)、流行度排名。复用 LCC(地理)、PROV-O(特征数据溯源,关联品种特征值与提供组织)、OMG Ratings(流行度排名)。用例为品种推荐系统 "Find a Friend"/"Find a Pet"(输入家庭/主人特征→推理→分类→推荐,含替代方案)。含 competency questions、SPARQL 查询演示、概念图、术语表、与 AKC/Bow Wow Meow/IAMS 品种选择器的对比评估。本体文件: find-a-pet.rdf, find-a-pet-individuals-small.rdf, find-a-pet-individuals.rdf。不含疾病/行为训练/饲养内容,聚焦品种匹配推荐。
- 备注: 已抓取 4 个页面核实: related_work.html(主URL)、项目 index.html、license.html、GitHub 仓库主页及 oe2022 目录。核实结论:描述基本属实——确为犬品种语义本体,复用 PROV-O/OMG Ratings/LCC 属实,建模脱毛/吠叫/儿童友好/可训练性/低敏属实,推荐系统用例属实(Find a Friend/Find a Pet)。存疑点:1) star=13 与 last_update 属父仓库(ontology-engineering 课程仓库)而非本项目,本项目为 oe2022 子目录下学生小组作业,无独立仓库/star/活跃度

### fishchen/dog-behavior-dataset 
- URL: https://huggingface.co/datasets/fishchen/dog-behavior-dataset
- 类型: dataset | 子领域: behavior (视频行为数据, 倾向 pose/姿态识别) | is_real: yes
- license: insufficient data (页面未声明 license, 无 dataset card) | 活跃: stale (月下载 3, 0 likes, 关联 Space 休眠, viewer 损坏未修复) | star: 0 likes (HuggingFace 用 likes 而非 star) | 更新: 最近一次上传约 2 个月前(相对抓取日, ~2026-05); 初始 commit 约 9 个月前(~2025-10); 仓库累计 2482 commits, 单一贡献者 fishchen
- 内容范围: 狗行为视频数据集。仓库结构: data/ 目录下含 videos/ 子目录(大量 .mp4 狗行为视频, 如 dog_1777388880739.mp4) + metadata.jsonl (212KB, JSON Lines 元数据)。总文件量 9.53GB。无 dataset card / README, 无行为分类标签说明。Dataset viewer 因 metadata 配置错误报错(file_name 必须作为 metadata 文件 key 存在), 无法预览。关联 Space "fishchen/dogspose"(休眠态) 暗示用途为狗姿态/行为识别。命名确为 dog behavior, 内容为真实狗行为视频原始数据, 非知识库/文档/本体。
- 备注: 核实结论: 确为真实狗行为数据集(yes), 但非"知识库/文档"型, 而是未加工的原始视频+JSONL 元数据, 9.53GB。无 README/dataset card/license/描述, viewer 损坏, 月下载仅 3, 0 likes, 关联 dogspose Space 休眠, 文档化与可用性极差。命名虽直指 dog behavior 但无任何行为分类/标注说明, 实际行为子类与标注体系无法从公开页面确认, 故标 uncertainty=true 待对抗核验。不适合作为对比报告重点(is_key_candidate=false): 体量虽大但无文档、无活跃度、无可用知识结构。

### juniorrios/icomp-dog-breed 
- URL: https://huggingface.co/datasets/juniorrios/icomp-dog-breed
- 类型: dataset | 子领域: breed | is_real: yes
- license: insufficient data(页面未标注 license) | 活跃: stale | star: 1 like, 59 downloads(last month) | 更新: 2023-06-15
- 内容范围: 狗品种图像分类数据集。20,579 张狗图片,单一 train split,724MB,以 dog-breed-identification.zip 上传(imagefolder 格式,自动转 Parquet)。源自 Kaggle 经典 Dog Breed Identification 数据集(120 品种)。仅含 image + label 两列,无文本/知识/行为/疾病/饲养等结构化信息。注意:HF 页面 label 列只显示 "2 classes" 且预览标签均为 "0test",与预期的 120 品种不符,疑为自动转换时标签未正确解析。
- 备注: 确为狗品种图像数据集,与已知描述(20.6k 样本)完全吻合。属计算机视觉分类数据集,非"知识库/文档/本体"——无行为/疾病/护理/训练等知识性内容,仅图片+标签。关键存疑点:HF 自动转换后的 label 列仅显示 "2 classes"(预览标签全为 "0test"),而 zip 文件名指向的 Kaggle dog-breed-identification 实为 120 品种数据集,二者矛盾,疑为 HF 端标签解析异常或上传者未正确配置 label classes,需对抗核验。活跃度低:仅 2 次 commit、1 like、59 downloads,3 年未更新,1 contribut

### benni-ben/dog-breeds 
- URL: https://huggingface.co/datasets/benni-ben/dog-breeds
- 类型: dataset | 子领域: breed (品种分类/识别) | is_real: yes
- license: MIT | 活跃: unknown | star: 1 (likes) | 更新: insufficient data (页面与 README 均未显示更新日期)
- 内容范围: 35,000+ 张狗图片,覆盖 390 个品种,按品种分文件夹组织(每品种 10+ 张),JPEG/PNG 格式,约 3.19GB。附带预训练 EfficientNet 分类模型(63% 准确率,TF/TFLite/TF.js/ONNX/Keras/CoreML 多格式)。仅图像分类任务,无品种行为/疾病/饲养/特性等文本知识。
- 备注: 真实狗品种图像数据集(35k+ 图片,390 品种,MIT),描述与实际相符,无伪装。但本质是图像分类数据集,非文本/事实型知识库——不含狗行为、疾病、饲养、品种特性等知识内容,仅有按品种命名的图片文件夹。数据集查看器损坏(ArrowInvalid/UnicodeDecodeError,二进制图片被当 JSON 解析)。热度低:1 like,月下载 48。对狗知识库对比报告价值有限,仅可作为"图像数据"类边缘示例,不作为重点候选。已抓取 HF 数据集主页 + raw README.md 两个佐证页,信息一致。

### Dewa/Dog_Emotion_Dataset_v2 
- URL: https://huggingface.co/datasets/Dewa/Dog_Emotion_Dataset_v2
- 类型: dataset | 子领域: behavior (emotion classification) | is_real: yes
- license: creativeml-openrail-m (页面显示为 creativl-openrail-m,疑为抓取拼写偏差) | 活跃: stale | star: 6 likes | 更新: 2024-04-10 (关联模型 Dog_Model_From_Scratch_v2 更新日期;数据集本身更新日期未在页面明确显示)
- 内容范围: 犬情绪图像分类数据集,4000张狗图片,4类情绪标签(0:sad悲伤/1:angry愤怒/2:relaxed放松/3:happy开心),3200训练+800测试,162MB,Parquet格式(自动转换),图片宽度100px~3.36k px,源自Kaggle数据集。任务类别:图像分类。模态:图像+文本标签。
- 备注: WebFetch 与 mcp__fetch__fetch 双重抓取结果一致,已知描述与实际内容完全吻合,无矛盾。数据集卡片极简(仅一句"基于Kaggle数据集"),无方法论/来源详细说明/作者信息,文档质量低。活跃度低(6 likes/142 downloads/月),最后更新约2024年4月,已超一年无更新。是真实的狗情绪数据集,但规模小、文档薄弱、不活跃,作为对比报告重点价值有限。确为狗专属数据集(exclusively dogs)。

### imixiu/paws-tales (Paws&Tales) 
- URL: https://github.com/imixiu/paws-tales
- 类型: mixed | 子领域: general(覆盖 care/training/behavior/health-disease,无单一专域) | is_real: yes
- license: 未声明(仓库无 LICENSE 文件) | 活跃: active(线上站 paws-tales.com 在持续每周更新文章;但 GitHub 仓库热度极低:0 star / 0 fork / 0 issue / 0 release / 22 commits) | star: 0 | 更新: insufficient data(主页仅显示 22 次提交,具体最近提交日期未在主页可见)
- 内容范围: 线上为狗护理期刊(paws-tales.com),实证文章覆盖:健康/疾病(蓝眼狗健康问题、犬种遗传病易感性、识别症状/病因/预防、何时就医)、训练(首次养主训练指南、食物攻击/资源守护、行为训练)、行为理解(读懂信号、狗的情绪科学)、护理(幼犬护理、养狗准备)、生活(旅行/假期/家庭)。6大分类:Training / Understanding Your Dog(行为) / Getting a Dog / Health & Wellbeing(兽医审核,含预警信号与生命周期健康) / Life With Your Dog / Puppy Care。非品种库或本体库,品种信息零散见于健康类文章。作者栏目自称由兽医/训练师/行为专家撰写。
- 备注: 核实结论:确为真实狗知识库/内容站(线上 paws-tales.com 抓取到真实狗文章:蓝眼狗健康问题、犬种遗传病易感性、首次养主训练指南、食物攻击训练、行为理解等),描述与实际相符。

关键限定(为何 is_key_candidate=false 且 uncertainty=true):
1. 仓库本身仅含 Next.js 应用代码,文章与作者数据存储在 MySQL(MYSQL_URL 环境变量)并用 Tair 缓存(lib/db.ts),知识内容不在仓库内——作为开源知识库不可移植/不可复用,无法离线审计文章语料。
2. README 是 create-next-app 默认样板,无项目

### Barkopedia_Dog_Sex_Classification_Dataset 
- URL: https://huggingface.co/datasets/ArlingtonCL2/Barkopedia_Dog_Sex_Classification_Dataset
- 类型: dataset | 子领域: behavior(vocalization/barking) + biology(sex);audio classification | is_real: yes
- license: MIT | 活跃: unknown(无更新日期,下载量低20/月,0 likes,属冷门;但数据集完整可用) | star: 0 likes; 20 downloads/月 | 更新: insufficient data(数据集页面未显示最后更新日期)
- 内容范围: 狗吠叫声音频数据集,用于基于叫声的狗性别分类(male/female)。共29,345条音频片段,来自156只个体狗、5个品种(柴犬/哈士奇/吉娃娃/德国牧羊犬/比特犬)。训练集26,895条(母13,567+公13,328),测试集2,450条(母1,271+公1,179,其中980条公开榜/1,470条私有榜)。标签人工生成并验证,train_labels.csv含audio_id和pred_dog_sex字段。覆盖方向:行为(发声/吠叫)+生物学性别,不涉及疾病/品种识别/饲养/训练知识。
- 备注: 真实狗相关音频数据集,Barkopedia Challenge的一部分(challenge主页https://uta-acl2.github.io/barkopedia.html)。WebFetch与mcp__fetch__fetch两次抓取信息一致,与已知描述(约29.3k样本、Barkopedia系列、基于叫声的狗性别分类)完全吻合,无营销夸大或矛盾。属专门狗数据集而非通用动物/同名无关项目。规模明确(29,345条/156只狗/5品种/1.56GB)、有MIT许可与人工验证标签,对"狗声音/行为识别"方向是典型对比对象,值得作为对比报告重点。注意:它是ML任务数据集(音频+标签),非文本

### lurnake/dog-breed-traits-data 
- URL: https://github.com/lurnake/dog-breed-traits-data
- 类型: dataset | 子领域: breed/behavior/general(品种分组+性格行为+生活兼容性;含结构化品种-性状映射,可视为部分ontology) | is_real: yes
- license: 非标准"open-source principles"且需署名(作者Joona Heino),无MIT/Apache等标准SPDX License文件,仓库根目录无LICENSE文件 | 活跃: stale | star: 0 | 更新: 2025-02-13
- 内容范围: 犬品种与特性数据集。6个JSON文件: dog-breeds.json(按传统分组如sporting_dogs列出品种), breed-characteristics.json(覆盖temperament_personality/behavior/living_compatibility的性状清单), trait-breed-similarity.json与breed-trait-similarity.json(AI生成的0-100品种-性状相似度评分,两种视图), breed-characteristics-with-embeddings.json与dog-breeds-with-embeddings.json(OpenAI text-embedding-3-large嵌入向量)。覆盖品种分组/性格行为/生活兼容性,均为AI合成数据而非专家策展。
- 备注: 核实通过,实际内容与已知描述一致,无营销夸大。关键特征: (1)6个JSON+README,确为狗品种/性格行为数据集; (2)数据为AI合成——相似度评分由Gemini-2.0-Pro-Experimental(02-05)直接打分(生产方案),嵌入用OpenAI text-embedding-3-large,非专家策展/非权威知识源; (3)规模小且不活跃: 0 star, 4次提交全部集中在2025-02-13单日,作者Joona Heino,自此后无更新(截至2026-07-06约1.4年未动); (4)License非标准,商用/合规需谨慎; (5)无代码/工具,纯数据集。作为对比报

### Dog Behavior Object Detection Dataset (Roboflow Universe) 
- URL: https://universe.roboflow.com/carl-m6y6w/dog-behavior-qwvgf
- 类型: dataset | 子领域: behavior | is_real: yes
- license: insufficient data | 活跃: unknown | star: N/A (Roboflow Universe datasets have no star mechanism; not a GitHub repo) | 更新: insufficient data
- 内容范围: 犬类行为目标检测图像数据集,用于计算机视觉行为识别模型训练。含50张图像(object detection 标注)。具体行为类别标签因Roboflow屏蔽自动抓取(403)无法获取,insufficient data。规模极小(仅50图),属个人上传数据集,非系统性犬行为知识库。
- 备注: 直接抓取 Roboflow Universe 页面返回 HTTP 403 Forbidden(同时尝试 WebFetch、mcp__fetch__fetch、app.roboflow.com 变体均被robots.txt Disallow 或 403 拦截)。改用 DuckDuckGo HTML 搜索(snippet)核实身份:数据集确为 "Dog Behavior Object Detection Dataset",作者 Carl (workspace carl-m6y6w),50 张图像,object detection 任务,明确针对犬类行为。已知描述(犬行为标注图像用于行为识别CV模型

### gsusI/dog-breeds-database 
- URL: https://github.com/gsusI/dog-breeds-database
- 类型: dataset | 子领域: breed | is_real: yes
- license: CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International,非商业用途,商用需另行授权) | 活跃: stale | star: 0 | 更新: 2026-04-14 (单一快照提交,1 commit,1 release 标签 "2026-04-14 dataset snapshot")
- 内容范围: 人工策展犬品种数据集。655品种(601已审reviewed / 42待审needs-review / 12种子seeded),数据来源为官方品种标准、注册机构页面、品种俱乐部。双格式发布: data/curated-breeds.csv(主数据)与 data/dogs.db(SQLite导出),附 schema.sql 表结构。每品种含溯源字段 source_registry 与 source_url,追踪数据来源。另含 ATTRIBUTION.md、CITATION.cff、checksums.txt、LICENSE。范围聚焦品种(breed)本体与注册标准,不含行为/疾病/饲养/训练等内容。作者 Jesus Iniesta,源于 GitLab 项目 wesolvers/jesusiniesta.es。
- 备注: 已知描述与实际仓库完全一致:655品种(601/42/12)、CSV+SQLite双格式、source_registry/source_url溯源字段均经原始README与GitHub主页双重核实。仓库为一次性快照发布(仅1次commit、0 star/0 fork/0 watcher、1个release标签),无社区采用与持续维护迹象,作者单人策展。类型为纯数据集(无应用代码,仅SQL schema)。非商业许可(CC BY-NC 4.0)限制了商用。内容真实且为狗专属知识库,但因极低活跃度与零社区关注,作为对比报告重点的价值有限——可作为"小规模人工策展品种数据集"的方法学案例(溯源字段设

### Kaggle Dog Behavior Analysis Dataset (arashnic) 
- URL: https://www.kaggle.com/datasets/arashnic/animal-behavior-analysis
- 类型: dataset | 子领域: behavior | is_real: yes
- license: CC BY-SA 4.0 | 活跃: stale | star: N/A(Kaggle数据集,无star;下载量3178,usability评分0.97) | 更新: 2022-06-25(version 2)
- 内容范围: 犬类行为分类数据集(非文本知识库)。45只中大型犬,佩戴两个ActiGraph GT9X Link传感器(3轴加速度计+3轴陀螺仪,100Hz采样),分别置于背部harness和颈部collar。在10m×18m测试场地完成7项任务:静态3项(sit/stand/lie down)+动态4项(trot/walk/play/treat-search),每项3分钟。行为通过双摄像机视频标注(Observer XT 10.5软件)。Ethogram含7种行为:Galloping/Lying on chest/Sitting/Sniffing/Standing/Trotting/Walking,每种附详细行为描述。目标为监督式ML行为分类(特征工程挑战)。总大小约1.85GB。
- 备注: 佐证来源:Kaggle官方API(/api/v1/datasets/view/)返回完整JSON元数据,含title/subtitle/description/license/lastUpdated/downloadCount/totalBytes等字段。Kaggle网页本体为JS渲染,WebFetch仅返回标题,但API数据充分佐证。

关键核验结论:
1. 确为狗数据集(yes):实际标题"Dog Behavior Analysis Dataset",45只犬类专属,非通用动物。用户URL slug为"animal-behavior-analysis"具误导性,但实际内容100%犬类。
2

### Dog Aging Project (DAP) 
- URL: https://dogagingproject.org/data-access
- 类型: dataset | 子领域: general | is_real: yes
- license: 无开源 license;数据受 DAP Data Use Agreement 约束,需申请+签署 DUA,通过 Terra 平台(Broad Institute)授权访问,仅限科研/课程/非营利用途;商业用途走独立谈判流程 | 活跃: active | star: 16 | 更新: 数据集每年发布一次(最新 2025 release,累积至 2024-12-31);网站持续更新(2026-06 仍有新科研文章);GitHub 仓库 70 commits,具体最新提交日期未在页面显示
- 内容范围: 美国最大犬类老龄化纵向社区科学研究数据集。核心为 Health and Life Experience Survey (HLES),含 200+ 问题,覆盖:Owner Contact、Dog Demographics、Physical Activity、Environment、Behavior、Diet(标准+综合)、Medications & Preventives、Health Status、Owner Demographics 共 9 大域。另含环境数据、生物样本(biospecimen)实验室结果。40,000+ 只犬(一项已发表研究明确为 40,367 只),数据 2020-2022 采集。设多个科学队列:Pack、Foundation Cohort、Precision Cohort、TRIAD Cohort(雷帕霉素双盲安慰剂对照临床试验)。每年发布 curated 数据集(2023/2024/2025 已发布,累积式)。codebooks 与 survey instruments 在 GitHub 公开仓库。
- 备注: 核实结论:已知描述与实际高度一致,无营销夸大。佐证:(1) data-access 页 meta description 与正文确认"anonymized variables collected from tens of thousands of dogs,数据类型含 survey/environmental/biospecimen lab results";(2) 申请流程四步:Complete Application → 签 DAP Data Use Agreement → 获 Terra 凭证 → Start doing science;申请入口 redcap.dogagingproje

### CeruleanBeaver/awesome-dogs 
- URL: https://github.com/CeruleanBeaver/awesome-dogs
- 类型: doc-kb | 子领域: general | is_real: yes
- license: CC0-1.0 (Creative Commons Zero / Public Domain Dedication) | 活跃: stale | star: 0 | 更新: 2023-06-02 (最近一次提交 "Update README.md",SHA ef2563c;至 2026/07/06 已约 3 年未更新)
- 内容范围: awesome-list 风格的狗相关资源精选目录,共 73 条目,分 6 大类:(1) Databases 26 条——金融(MyPetChild/NAPHIA)、食品(DogFoodAdvisor/PetFoodIndustry/EWG Food Scores/Seafood Data)、遗传(Penn Vet/Dog Aging Project/NHGRI Dog Genome Project)、人狗互动(AWI/Animal Science/HABRI/Dogsbite/Infodog/Shelter Animals Count/BringFido/PetFriendlyTravel)、媒体(Stanford Dog Dataset/Audio Cats and Dogs)、医疗(Physionet/VeterinaryPartner)、走失宠物(Pet FBI)、寄生虫(WormBase ParaSite/Global Mammal Parasite Database)、感官(OlfactionBase)、污渍(Stain Solutions);(2) Education 6 条——Coursera 狗情绪与认知(Duke)、动物行为与福利(Edinburgh)、The Truth About Cats and Dogs(Edinburgh)、EdX 狗行为问题与解决(ASU)、瓦赫宁根动物育种证书、The Science Bank;(3) Literature 5 条——挑战品种刻板印象的ancestry-inclusive基因组学论文、Institute of Canine Biology、DOG-SPOT关系数据库论文、开源软件资助十则、狗皮层fMRI解码自然视频;(4) Miscellaneous 4 条——毒物控制、仿真、视频、白噪音;(5) Projects 6 条——Doggy Door安防与宠物追踪、Arduino/RPi宠物监控、TinyML狗叫停止器、计算机控制零食分发器、DogOnMat、Metafluidics;(6) Software 26 条——领养(Adoptable pet bot)、AI(DeepLabCut/MONAI/GeoCam)、API(Petfinder/Dog Facts)、生物信息(QIIME 2/PhysioZoo)、交友(Woofie)、家庭(OpenHAB/Hass TryFi/Anymeal/VenomMaps)、ML(PawPal/Kaggle品种识别/dogTorch/Dogspotting/狗叫检测/Pet Pawpularity)、血统(Open Pedigree/Doggo)、摄影(Pet Focus)、兽医(VetGeo/OpenVPMS/VetteV/DCM4CHE)。覆盖行为/疾病遗传/品种/饲养/训练/通用多子域,无独立本体(ontology)分类。本身是链接目录(meta-resource/顺藤摸瓜入口),非原始数据或代码。
- 备注: 核实结论:确为狗相关资源精选目录(awesome-list),73 条目与已知描述完全一致,6 大类结构清晰,CC0 公共领域许可,内容真实。但定位为"顺藤摸瓜入口"(meta-resource/链接目录),本身不含狗知识结构化数据或本体,而是聚合外部数据库/课程/文献/软件的导航索引。活跃度低:0 star、最近提交 2023-06-02、约 3 年未更新,属 stale 个人小仓库。涵盖行为/疾病遗传/品种/饲养/训练/通用多子域但每项深度浅(仅链接+简述)。对狗知识库对比报告价值:可作为"资源发现入口"提及,但不值得作为重点对比对象(内容浅+不活跃+无原创数据)。已知描述"73条目/含数

### umuttuygurr/videosdog (Real-World Dog Behavior Videos) 
- URL: https://www.kaggle.com/datasets/umuttuygurr/videosdog
- 类型: dataset | 子领域: behavior | is_real: yes
- license: CC0: Public Domain | 活跃: active | star: 3 (votes/likes) | 更新: 2025-12-09 (version 2)
- 内容范围: 64 个室内俯视(鸟瞰)摄像头长视频,记录同一只狗的日常行为,总大小 1.42 GB。覆盖行为:睡眠/休息、室内移动、站立/转身/重新定位、与食盆互动。视频未标注(无人工标签),适合无监督/自监督/弱监督学习。潜在用途:动物行为分析、活动/休息检测、睡眠状态分类、运动检测与背景减除、光流与移动跟踪、自监督表征学习、帧提取与视频预处理。录制设置:固定头顶摄像头、俯视、室内极简背景、单只狗(同一只)、有食盆。
- 备注: 真实狗行为视频数据集,Kaggle 页面 schema.org JSON-LD 元数据与 API 一致,描述与实际相符,无营销夸大。规模偏小:仅 64 个视频、单只狗(同一只个体)、无人工标注、仅室内俯视场景,行为类别仅 4 类(睡眠/移动/站立转身/食盆互动),内容范围相对窄。统计:152 下载、1112 查看、3 票、0 评论、2 个关联 notebook。CC0 公共领域许可,可自由使用。创建者 UmutUygurr。作为对比报告的补充数据点(真实狗行为视频数据集案例)有价值,但因规模小、单狗、无标注、范围窄,不宜作为重点对比对象。适合无监督/自监督学习研究,不适合需要标注的监督学习任务

### Morevorot/Dog_breed_Japanese_Spitz 
- URL: https://huggingface.co/datasets/Morevorot/Dog_breed_Japanese_Spitz
- 类型: dataset | 子领域: breed | is_real: yes
- license: cc-by-sa-4.0 (WebFetch提取;原始fetch页面License段值未清晰渲染,略有不确定性) | 活跃: stale | star: 0 likes (HF用likes非star);Downloads last month: 5 | 更新: insufficient data (页面未显示明确最后更新/提交日期)
- 内容范围: 单一犬种图像数据集:日本狐狸犬(Japanese Spitz)品种图片,共3,497张(约3.5k),parquet格式,总7.36GB,单列image,单subset(default)/单split(train),分辨率>256x256,无1:1复制但有同源处理版本,文件名序号化。创作者标注了632/639/640/644/1003/1810/2000行为误标品种。仅图像,无结构化知识/文本元数据,非知识库,可用于细粒度品种识别/分类。无行为/疾病/饲养/训练等知识内容。
- 备注: WebFetch与mcp__fetch__fetch双重抓取一致,均success。确为真实HF数据集,非编造。已知描述(日本狐狸犬,约3.5k样本)与实际(3,497行)吻合,无矛盾。属纯图像分类数据(单一品种),非狗知识库/文档;作为"狗知识库对比报告"重点价值低:无结构化知识、无文本、无行为/疾病/护理/训练内容,0 likes+5下载/月,活跃度低。License值(cc-by-sa-4.0)由WebFetch提取,原始fetch未清晰渲染该字段,但其余维度双重印证,uncertainty设为false。该数据集是"狗相关"但非"狗知识库",若报告聚焦知识库/文档类则不作为重点候选。

### waqi786/dogs-dataset-3000-records (Kaggle) 
- URL: https://www.kaggle.com/datasets/waqi786/dogs-dataset-3000-records
- 类型: dataset | 子领域: breed | is_real: yes
- license: Apache 2.0 | 活跃: stale | star: 31 (likes); 2258 downloads; 11064 views; 1 comment | 更新: 2024-07-30 (dateModified, version 1, 自此无更新)
- 内容范围: 综合犬只表格数据集,共3000条记录,仅5个字段:Breed(品种,如拉布拉多/比格/金毛/德牧)、Age(1-15岁)、Weight(5-60kg)、Color(黑/白/棕/金/斑点)、Gender(公/母)。用例:品种分布分析、体重年龄相关性、犬只分类预测模型、可视化仪表板、犬种识别AI训练。关键限制:数据为合成生成(synthetically generated),非真实世界数据,仅模拟犬只特征,用于教学与分析练习。不含行为/疾病/护理/训练/本体等知识内容。
- 备注: 抓取方式:Kaggle页面为JS渲染,WebFetch与mcp__fetch__fetch的markdown模式仅得标题;改用raw=true获取原始HTML,从中提取<script type="application/ld+json">中的schema.org Dataset JSON-LD元数据,信息完整可信。

核实结论:确为狗数据集(is_real_dog_kb=yes),内容与描述基本一致——3000条狗记录。但三个重要限定:
1) 数据为合成生成(synthetically generated),非真实世界数据,作者明确声明仅供教学分析;
2) 仅5个基础字段(品种/年龄/体重/颜

### FengChen-406/dog-knowledge-base 
- URL: https://github.com/FengChen-406/dog-knowledge-base
- 类型: doc-kb | 子领域: general (care/breed/training/health 综合入门科普) | is_real: yes
- license: MIT | 活跃: stale | star: 1 | 更新: 2024 (仅 1 次 commit,copyright 2024-present,自 2024 后无更新,截至 2026-07 已 stale)
- 内容范围: VuePress 文档站,养狗科普知识库。首页声明三大板块:科学养护(日常喂养到疾病预防)、行为训练(训练方法与习惯培养)、健康指南(健康知识与常见疾病预防)。实测 docs/basics/README.md 含真实内容:养狗前准备(时间/环境/经济/家庭)、选择适合犬种(按生活环境与个人情况,含拉布拉多/金毛/柴犬/泰迪/边牧介绍)、必备用品清单(基础用品/清洁用品)。覆盖 care/breed/training/health,属 general 综合型,非疾病或行为单一深度专题。内容偏入门科普,深度有限。
- 备注: 核实结论:确为真实狗知识库(VuePress 文档站,MIT,狗专属),描述与实际一致,无营销夸大,抓取信息无矛盾。但作为对比报告重点价值低:仅 1 star/1 commit/0 fork/0 issue,单作者 hobby 项目,内容为入门科普且实测仅 basics 一页有实质内容,深度与体量均不足,活跃度 stale。根目录无 README.md(raw HEAD/master 均 404),首页内容实为 docs/README.md 的 VuePress frontmatter;docs/.vuepress/config.ts 亦 404(配置可能为 .js 或未提交)。fetch 整

### ArlingtonCL2/Barkopedia-Dog-Vocal-Detection 
- URL: https://huggingface.co/datasets/ArlingtonCL2/Barkopedia-Dog-Vocal-Detection
- 类型: dataset | 子领域: behavior (vocalization) + breed | is_real: yes
- license: 未在页面明确标注 (unspecified) | 活跃: active (有持续下载量346/月,配套Challenge) | star: 3 likes; 346 downloads/last month | 更新: insufficient data (页面未显示commit/update日期)
- 内容范围: 狗发声检测(dog vocalization detection)音频数据集。标注类别:dog(连续吠叫)、dog_noise(吠叫伴随明显噪声如人声/环境声)。含约7500秒强标注训练音频、9000+秒弱标注片段(来自AudioSet)、24小时无标注音频。部分片段含狗但无吠叫以模拟真实场景。按品种分文件夹:chihuahua/german_shepherd/husky/labrador/pitbull/shiba_inu。TSV格式:filename/onset(s)/offset(s)/label。服务于Barkopedia Dog Vocal Detection Challenge。
- 备注: 真实存在的狗发声检测音频数据集,由Arlington Computational Linguistic Lab (ArlingtonCL2)发布。确为狗专用(yes),非通用动物。547行(validation 200 + test 347),总文件6.5GB,Size category < 1K,Tags: audio-event-detection,Modality: Audio,Format: soundfolder,Libraries: Datasets/Croissant。属Barkopedia系列。注意:此为音频事件检测数据集(行为/发声),非文本知识库/文档;样本量较小(547行

### Dog voice emotion dataset (Demo-Lite) 
- URL: https://www.kaggle.com/datasets/shivarao100/dog-voice-emotion-dataset
- 类型: dataset | 子领域: behavior (情绪/发声 emotion & vocalization) | is_real: yes
- license: Apache 2.0 | 活跃: stale | star: 9 (Kaggle upvotes) | 更新: 2024-09-14 (v1 Initial release,此后未更新)
- 内容范围: 狗叫声/语音情绪识别音频数据集。含163条狗叫声录音,分为4种voice类型(情绪类别),用于狗叫声情绪分类(Classification of Dog voice emotion)。为纯音频数据集,无文本知识/文档/本体。规模约57MB。属Demo-Lite精简版。
- 备注: 通过Kaggle官方API获取权威JSON元数据成功(主页WebFetch仅返回标题,因Kaggle页面JS渲染+需登录;改用API端点+原始HTML中的schema.org JSON-LD获取完整数据,二者一致)。

确认结论:确为狗专用数据集——狗叫声情绪分类音频,163条录音/4类情绪/Apache 2.0/~57MB/2024-09-14初始发布v1后未再更新。描述与已知"Demo-Lite版,叫声情绪识别"完全吻合,无矛盾。

不作为对比报告重点的原因:(1)规模极小,仅163条录音;(2)可用性评分仅0.4375/1.0,元数据不完善、无标签;(3)0讨论/0评论,社区参与度低;(

### paiv/fci-breeds 
- URL: https://github.com/paiv/fci-breeds
- 类型: dataset | 子领域: breed | is_real: yes
- license: MIT | 活跃: active | star: 48 | 更新: 2025-12-06(release 1.15.0);共32次提交
- 内容范围: FCI(Fédération Cynologique Internationale)国际犬业联合会认可的犬种结构化数据集。9字段:id/name(品种名)/group(FCI分组,如Pointing Dogs/Terriers/Retrievers)/section(分区)/provisional(临时认可日期)/country(原产国)/url(FCI命名法页面)/image(插图URL)/pdf(品种标准PDF链接)。共360个犬种(ID 1-374,14个未分配)。覆盖6种语言:EN/FR/DE/ES来自fci.be官方,PL来自zkwp.pl,UK来自uku.com.ua。含配套Python生成代码与GitHub Actions工作流。不涉及行为/疾病/饲养/训练,纯品种分类本体数据。
- 备注: 三次抓取(GitHub repo主页/raw README/raw CSV)全部成功且数据自洽,描述与实际完全相符,无营销夸大。亮点:①数据源权威(FCI官方+国家犬业俱乐部);②多语言(6种);③结构化程度高(9字段含FCI分组/分区/原产国/标准PDF链接);④活跃维护(2025-12最新release);⑤MIT许可可自由复用。局限:仅品种名录与分类本体,无行为/疾病/饲养/训练等知识维度,适合作为"品种知识库/本体"对比项,非全维度狗知识库。Demo站点:paiv.github.io/fci-breeds。

### Movement Sensor Dataset for Dog Behavior Classification 
- URL: https://data.mendeley.com/datasets/vxhx934tbn/1
- 类型: dataset | 子领域: behavior | is_real: yes
- license: CC BY 4.0 | 活跃: stale | star: N/A (Mendeley Data 无 star 机制) | 更新: 2021-07-02 (Version 1, 此后无更新)
- 内容范围: 犬类行为运动传感器数据集。ActiGraph GT9X Link 传感器同时佩戴于项圈(collar)和胸背带(harness),含3D加速度计+3D陀螺仪,100Hz采样率。7类行为标注:galloping(疾走/飞奔)、lying on chest(趴卧)、sitting(坐)、sniffing(嗅)、standing(站)、trotting(小跑)、walking(走)。用于犬类行为分类模型训练与可穿戴活动识别研究。非知识库型,为传感器原始/标注时序数据。
- 备注: DOI: 10.17632/vxhx934tbn.1。2021-07-02 发布,Version 1,此后无更新(stale)。11位贡献者来自芬兰多个机构,含 Outi Vainio(赫尔辛基大学知名犬类研究者)。关联两篇同行评议论文:(1) Vehkaoja 等, Description of Movement Sensor Dataset for Dog Behavior Classification, Data in Brief, 2021(数据描述);(2) Kumpulainen 等, Dog behaviour classification with movement senso

### leelaunches/holihounds 
- URL: https://github.com/leelaunches/holihounds
- 类型: doc-kb | 子领域: general (dog-friendly travel/accommodations;含 care 牵绳/围栏安全、breed-related greyhound 实操) | is_real: yes
- license: insufficient data (README 与 repo 页面均未声明 license) | 活跃: unknown | star: 0 | 更新: main 分支共 11 commits,具体日期 insufficient data;状态为 Sprint 1 build-complete,待办含 Awin 商家审批、占位图替换、Google Search Console 提交
- 内容范围: 英国狗友好旅行指南,editorial 编辑性内容库。当前覆盖:康沃尔地区(12 条已核实小屋 cottage)、英国 16 条热水浴缸度假屋 lodge、酒馆 pub(在 schema 结构中)、9 个通用狗友好旅行页面。每条房源含核实过的狗政策细节:牵绳要求(on-lead)、围栏侧隙(side gaps in fences)、度假村状态(holiday-park)、海滩通道、距离、设施。核心编辑原则"Every concrete detail traces to source",模糊来源标注"varies by property"或"not stated on the public listing"而非编造。含 JSON-LD 结构化数据(Article/ItemList/FAQ)、内容集合 schema(regions/listings/pages)。作者 Rachel Polden(养两只退役赛灵缇 greyhound),British English,ASA 联盟披露合规。
- 备注: 与已知描述高度吻合,无矛盾或营销夸大。确为真实的狗主题文档型知识库(doc-kb):Astro 6 + Tailwind v4 (PostCSS) + MDX 技术栈,Cloudflare Pages 部署,holihounds.com 主域。内容架构清晰(content.config.ts 定义 regions/listings/pages collections,每条 listing 一个 MDX/markdown),溯源标准严谨(Lighthouse 100/100/100/100)。但规模小且处于初期:仅康沃尔一个地区、12 条小屋、16 条 lodge、0 star、0 fork、S

### American-Kennel-Club-Breeds-by-Size-Dataset 
- URL: https://github.com/MeganSorenson/American-Kennel-Club-Breeds-by-Size-Dataset
- 类型: dataset | 子领域: breed | is_real: yes
- license: 无(license: null,未声明许可证,默认 all rights reserved) | 活跃: stale | star: 8 | 更新: 代码最后推送 2021-08-23(pushed_at),仅 1 次提交;元数据 updated_at 2026-05-19(仅 star 等非代码更新)
- 内容范围: 单一 Excel 文件(AmericanKennelClubBreedsBySize.xlsx),收录 AKC(美国犬业俱乐部)认可的犬种并按体型(size)分类。数据采集自 https://www.akc.org/dog-breeds/ 。仅覆盖品种+体型维度,不含行为/疾病/护理/训练/本体等信息。无 README,无数据字典,字段细节不可见(未公开 xlsx 内部结构)。
- 备注: 核实结论:确为狗相关数据集(AKC 犬种按体型分类),is_real_dog_kb=yes。但作为对比报告重点价值低:(1) 体量极小——单文件 xlsx,仓库 21KB;(2) 无 README、无数据字典、无字段说明,可用性差;(3) 无许可证,再利用受限;(4) 严重 stale——2021-08-23 创建并仅推送 1 次后再无代码更新,距今约 5 年;(5) 仅 8 star/1 fork,社区关注度低;(6) 仅品种+体型维度,不含行为/疾病/护理/训练,覆盖面窄。描述与实际一致,无营销夸大,无需对抗核验。README 抓取失败属真实情况(文件不存在),非抓取故障。

### Sujimirutikaa/Pet-Care-Advisor 
- URL: https://github.com/Sujimirutikaa/Pet-Care-Advisor
- 类型: mixed | 子领域: disease/care | is_real: partial
- license: MIT | 活跃: stale | star: 0 | 更新: 2026-01-26 (最新commit); 仓库创建于 2025-11-20,共6次commit
- 内容范围: 宠物(含狗与猫)常见健康问题诊断:根据用户输入症状推理诊断、给出护理/治疗建议、提示何时需就医。基于 knowledge_base.json 结构化知识库 + 推理规则的专家系统,含 Flask 后端(app.py/config.py/app/)与 HTML/CSS/JS 前端(含 landing page)。测试样例同时含狗(癫痫/昏迷)与猫(呕吐/拒食)。无行为/品种/训练/本体内容。知识库具体条目数与结构 README 未披露。
- 备注: 已知描述"Flask 宠物健康问题诊断知识库 AI 代理"与实际高度一致,无夸大或张冠李戴。实为通用宠物(狗+猫)健康诊断专家系统,非狗专用知识库,故 is_real_dog_kb=partial。规模小:0 star、6 commit、单人(Sujimirutikaa)短窗口内完成,属个人/课设级项目。知识库为 JSON+推理规则形式,但条目规模与覆盖病种数未在 README 披露,知识库深度存轻度未验证(不影响描述真实性)。作为狗知识库对比报告重点价值有限:体量小、非狗专属、内容维度单一(仅疾病/护理),建议仅作"通用宠物健康KB"参考案例,不作重点。三处抓取(repo主页/README/

### Vertebrate Breed Ontology (VBO) 
- URL: https://github.com/monarch-initiative/vertebrate-breed-ontology
- 类型: mixed | 子领域: ontology/breed | is_real: partial
- license: CC-BY 4.0 | 活跃: active | star: 16 | 更新: 2026-04-15 (v2026-04-15 latest release; 416 commits on master)
- 内容范围: 脊椎动物品种标准本体(Ontology)。以FAO DADIS数据库(8800+品种/38物种)为基础,扩展加入DADIS未覆盖的品种(如猫),收录所有OMIA/AHIDA相关物种的品种名及同义词。狗是重点覆盖物种之一:最新release为292个dog breed terms添加foundation stock关系、为3个品种添加AKC认可状态(含Teddy Roosevelt Terrier)、VeNom集成新增2个dog breeds。本体用途:OMIA与AHIDA兽医健康记录的品种数据互操作、品种名标准化与同义词映射、LBO/OMIA ID映射到VBO ID。输出多种格式(OWL/OBO/JSON)的vbo-base/vbo-full/vbo-simple版本。注意:这是全脊椎动物品种本体(覆盖49物种),狗只是其中一大类,非狗专属知识库。
- 备注: 三路抓取(GitHub主页WebFetch、raw README WebFetch、mcp__fetch__fetch原始页)结果一致,信息充分。已知描述与实际核对:(1)"17个release"已直接核实(Releases 17,跨2023-06至2026-04);(2)"19500+品种概念/49物种"未能从README直接核实——README只列DADIS本身的8800 breeds/38 species,但VBO通过同义词+非DADIS品种(如猫)扩展,故19500+/49属合理推估值,非矛盾;(3)狗覆盖由release notes明确证实(292 dog breed foundat

### ewwerpm/dog_no_barking 
- URL: https://huggingface.co/datasets/ewwerpm/dog_no_barking
- 类型: dataset | 子领域: behavior | is_real: partial
- license: insufficient data（未指定） | 活跃: stale | star: 0 likes | 更新: insufficient data（页面未显示明确提交/更新日期）
- 内容范围: HuggingFace 数据集，描述为"整理的不包含狗叫的音频"，即排除犬吠声的过滤音频集合。仓库实质为空（总大小约 2.34 kB，无数据文件上传），无 license，无 yaml metadata，dataset card 显示"The dataset is currently empty"。无 README/dataset card 实质内容。仅作为狗叫检测/犬吠识别任务的负样本或背景音频有间接关联，本身不含狗行为/疾病/品种/饲养/训练等知识数据。统计：0 likes，4 downloads/month。
- 备注: JSON-LD 结构化数据与页面渲染描述一致，均为"整理的不包含狗叫的音频"，描述与实际无矛盾。该数据集本质是"排除狗叫的音频"过滤集，与狗知识库关联仅在于其作为狗叫检测任务的负样本/背景音频的间接用途，本身不含狗相关知识点。仓库为空壳，无任何数据文件、无 license、无 metadata、无 README，0 likes/4 downloads，活跃度极低，不建议作为对比报告重点。归类为 partial：与犬吠声/狗叫行为检测任务存在边缘相关性，但非狗知识库/文档/数据集（内容是"非狗叫"音频）。

### feiwu77777/animime-dog-breeds 
- URL: https://huggingface.co/datasets/feiwu77777/animime-dog-breeds
- 类型: dataset | 子领域: breed | is_real: partial
- license: Research / non-commercial (Stanford Dogs terms of use), HF页面标注为 "other" | 活跃: stale | star: 0 | 更新: insufficient data (页面未显示明确更新日期)
- 内容范围: 10个狗品种图像分类数据集:beagle, boxer, chihuahua, german_shepherd, golden_retriever, husky, labrador, poodle, pug, rottweiler。共1,674张图片(train约1340/val165/test174,80/10/10分割,seed=42),总大小62MB,ImageFolder布局,已自动转Parquet。图片宽度142px-3260px。仅含图片+品种标签,无行为/疾病/饲养/训练等知识性文本内容。
- 备注: 源自Stanford Dogs数据集(Khosla et al., CVPR 2011, http://vision.stanford.edu/aditya86/ImageNetDogs/)的过滤子集,重新切分为train/val/test。本质是图片分类训练数据,为animime分类器服务(过滤切分脚本在animime_model repo的scripts/download_datasets.py)。判断为partial而非yes:虽确为狗品种数据集,但仅含图片+品种标签,无知识库/文档性质内容,且用途为图片品种分类(接近no例子"狗图片分类器")。已知描述"约1.67k样本"与实际1674

### PrimPetCare (syedazobiarizvi-sudo/primpetcare.github.io) 
- URL: https://github.com/syedazobiarizvi-sudo/primpetcare.github.io
- 类型: doc-kb | 子领域: general/care | is_real: partial
- license: insufficient data (仓库未指定 license) | 活跃: stale | star: 0 | 更新: insufficient data (主页仅显示 "1 Commit",未显示具体日期)
- 内容范围: README 仅一段描述性文字,列举主题涵盖 dog care、cat care、pet health、nutrition、grooming、training、wellness。非犬专项,为通用宠物(猫+狗)。无疾病(disease)、无品种(breed)专题。仓库实际仅含 README.md 单文件,无 HTML/CSS/JS 网页、无数据集、无文档目录、无实际文章或结构化知识库内容。本质为空壳 skeleton 仓库,仅声明意图未落地任何实质知识资源。
- 备注: 两次抓取(GitHub 主页 + raw README)均成功并相互印证。核心结论:此仓库非真实狗知识库,而是几乎为空的 skeleton 仓库,仅含一段描述性 README,无任何落地内容(无网页、无数据集、无文档目录、无文章)。已知描述"面向宠主的可信狗护理信息资源站"及类型 doc-kb 属营销性夸大,与实际严重不符。具体维度:0 star / 0 fork / 0 watching / 仅 1 commit / 无 license / 无 contributors / 无 releases / 无编程语言。主题范围通用宠物(含猫),非犬专项,故 is_real_dog_kb=parti

### JackyeC/keep-waco-wagging 
- URL: https://github.com/JackyeC/keep-waco-wagging
- 类型: mixed | 子领域: general | is_real: partial
- license: 无(未声明 license,无 LICENSE 文件) | 活跃: active | star: 0 | 更新: 2026-07-05 (commit: "feat: deploy Batch 2B shop funnel analytics", SHA edcc260)
- 内容范围: Waco, Texas 地区狗友好生活方式指南网站。内容覆盖:狗友好商家目录(patio/park/trail)、"Where to Wag This Weekend"周末活动指南、生活方式狗训练内容(lifestyle dog training)、宠物提交墙(Wagging Wall)、Amazon affiliate 装备店、本地商家聚光灯、博客、Platinum Scoops 赞助页。另有 lead capture 表单(通讯订阅/Get Listed/宠物提交)经 Supabase,邮件通知经 Resend。不含疾病、品种、ontology 等科学/兽医内容,偏本地商家目录与商业引流。
- 备注: 本质是 Platinum Scoops(pet waste removal + lifestyle dog training 商业)的客户获取/营销网站 + 本地狗友好商家目录 + 生活方式内容站,非传统"狗知识库/文档/数据集"。设计成可复制到其他城市的模型(city cloning checklist)。专门围绕狗(yes),但内容偏商业引流与本地目录,无疾病/品种/行为科学/ontology 维度,故 is_real_dog_kb=partial。技术栈现代(Next.js 16),项目活跃(昨日仍有提交,共 66 commits),但 0 star/0 fork/0 watching,

### Mammalian Phenotype Ontology (MP) 
- URL: https://github.com/mgijax/mammalian-phenotype-ontology
- 类型: mixed | 子领域: ontology | is_real: partial
- license: CC-BY-4.0 (主页显示;README未提及license) | 活跃: active | star: 20 | 更新: v2026-06-17 (release日期2026-06-18);main分支3,536 commits
- 内容范围: 哺乳动物表型标准化术语本体(OBO/OWL/JSON格式),提供表型标注词汇,覆盖哺乳动物表型术语(形态/生理/行为/疾病等表型术语),通过PURL(purl.obolibrary.org/obo/mp.obo)和MGI FTP分发,被OBO Foundry收录。README完全不提狗/canine,无专门犬类内容,主要与MGI(Mouse Genome Informatics小鼠基因组信息学)关联,服务小鼠研究社区。
- 备注: 已知描述称"覆盖犬类"在抓取中未得证实——README完全不提dog/canine,项目主要与MGI(小鼠基因组信息学)关联,被IMPC国际小鼠表型联盟使用,本质是小鼠/哺乳动物表型标准术语本体。分类学上"哺乳动物"含犬科,理论可标注狗表型,但无任何专门犬类内容,故判partial非yes。描述与实际存在差异(夸大犬类覆盖),需对抗核验。活跃项目(2026-06仍在更新,3536 commits,CC-BY-4.0)。不适合作为狗知识库对比报告重点,但可作为"哺乳动物表型标准术语"背景参考。两次WebFetch(GitHub主页+raw README)均成功。

### Jofleming/canine_disease_prediction 
- URL: https://github.com/Jofleming/canine_disease_prediction
- 类型: code | 子领域: disease | is_real: partial
- license: 无/未指定(Public 仓库但无 LICENSE 文件) | 活跃: stale | star: 0 | 更新: 2026-02-26(唯一一次 commit,message: "pushing up project to github")
- 内容范围: 犬类疾病预测 ML 项目。基于 Kaggle "Animal Disease Prediction" 数据集(原拟用 Dog Aging Project 数据集,因访问限制改用 Kaggle),过滤为犬类子集。将疾病标签归为三类临床分类:GI(胃肠)/Infectious(感染)/Other_Group(其他)。方法:Logistic 回归作 baseline(准确率~0.33,加权 F1~0.32),随机森林经超参调优(准确率~0.47,加权 F1~0.47)。含 final.ipynb 代码 notebook、cleaned_animal_disease_prediction.csv 清洗数据集、README,以及混淆矩阵/特征重要性图(文件名带 dog 前缀如 confusion_matrix_dog_3class.png)。覆盖数据清洗、类别编码、train/test 划分、模型训练与评估。
- 备注: 犬类特异(canine-specific):明确过滤多物种数据集为 dog subset,输出文件带 dog 前缀,确为犬类疾病相关。判 partial 而非 yes 的理由:(1) 本质是个人 ML 代码实验项目(type=code),非作为"狗知识库/数据集"产品发布;(2) 数据源为第三方 Kaggle 且明确声明"不可再分发(redistribution restricted by dataset license)",作为狗数据集复用价值有限;(3) 模型准确率低(~0.47),疾病分类为粗粒度 3 类而非结构化疾病知识。描述与实际高度吻合:犬类子集/Logistic+随机森林/GI/

### Animal Veterinary Health Dataset (sathwiknomula) 
- URL: https://www.kaggle.com/datasets/sathwiknomula/animal-veterinary-health-dataset
- 类型: dataset | 子领域: disease (妊娠相关疾病:Brucellosis/Toxoplasmosis/Pyometra) + general veterinary (多物种生殖健康) | is_real: partial
- license: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/) | 活跃: active (2025-08 更新,但互动极低:2 likes / 745 downloads / 0 comments) | star: 2 likes (Kaggle 无 star,用 likes 计;745 downloads, 4037 views, 0 comments) | 更新: 2025-08-15 (dateModified: 2025-08-15T14:19:56Z, version 2)
- 内容范围: 兽医健康表格数据集(v2,~57KB zip)。含动物物种特异性健康指标、妊娠状态、分娩日期预测、症状、疾病诊断记录。目标用于构建 AI/ML 系统:预测动物妊娠状态、估算分娩日期、检测妊娠相关疾病(Brucellosis 布鲁氏菌病、Toxoplasmosis 弓形虫病、Pyometra 子宫蓄脓)、兽医决策支持。多物种通用,非犬专属;但 Pyometra/Brucellosis 对犬高度相关。非知识库/文档,为结构化 ML 训练数据。
- 备注: 抓取方式:WebFetch 仅返回标题(JS 渲染页面正文缺失),改用 mcp__fetch__fetch raw=true 获取原始 HTML,从 <script type="application/ld+json"> schema.org Dataset 块提取完整元数据,信息可靠。非 GitHub repo,故未抓 README。判断依据:描述明确为通用动物兽医数据(含 species-specific 多物种指标),未特指犬;但所涉疾病 Pyometra(子宫蓄脓)为犬典型疾病、Brucellosis(布鲁氏菌病)亦感染犬,故标 partial 而非 no。非知识库/文档/本体,而是小

### lpastor75/dog-breed-classification 
- URL: https://huggingface.co/datasets/lpastor75/dog-breed-classification
- 类型: dataset | 子领域: breed | is_real: partial
- license: 未标注(not specified) | 活跃: stale | star: 1 like | 更新: commit d2d5d29,约2个月前(相对时间,无绝对日期)
- 内容范围: 狗品种图像分类数据集(CV训练数据),非知识库/文档/本体。含12,891张RGB狗图像,74个品种类别,多分类任务。结构:train.csv(8.99k)/valid.csv(1.89k)/test.csv(2.01k)+dog-images.zip,共493MB。仅含图片+品种标签,无行为/疾病/饲养/训练/本体等知识性文本。目标:训练深度学习模型从单张图像识别狗品种。README为西班牙语,兼容TensorFlow/PyTorch/HuggingFace。
- 备注: 确为真实狗相关数据集,与已知描述(12.9k样本/狗品种分类)完全一致,无夸大。但本质是图像分类训练数据(图片+品种标签),非"知识库/文档/本体",不含行为/疾病/饲养/训练等知识性内容,对"宠物行为知识库"对比报告参考价值有限,不作为重点候选。双重抓取(主页WebFetch+README原文mcp__fetch)信息一致。license缺失、仅1 like、最近提交约2个月前、无持续更新,判为stale。

### dog-behavior-dataset-creation-tools 
- URL: https://github.com/giovanni-gallerani/dog-behavior-dataset-creation-tools
- 类型: tool | 子领域: behavior | is_real: partial
- license: CC-BY-4.0 | 活跃: stale | star: 0 | 更新: insufficient data — 仓库仅4次提交,无明确最新提交日期;README自述项目仍在TTLab官方仓库演进,本仓库为论文快照
- 内容范围: 犬行为研究 BIDS 数据集创建工具集。包含 docs/(硕士论文PDF + 数据集结构文档) 与 code/(Python脚本)。代码覆盖:participant_adder.py(添加被试)、commander.py(LSL触发)、recorder_audio_video(双相机+麦克风+无线麦录制)、recorder_ecg_mpu(ECG+MPU运动传感器录制,需定制硬件)、safely_merge_dataset(合并.tsv)、annotate_dataset(添加BIDS元数据)、dataset_utils.py、audio_and_video_utilities/、dataset_description_files_templates/。多模态生物信号(心电/运动/音频/视频)采集 + BIDS标准化元数据标注。本身是空脚手架+工具,非已填充数据集。
- 备注: TUAT(东京农工大学)生物信号信息学实验室硕士论文成果,作者giovanni-gallerani。确为犬行为研究专用工具:采集犬的多模态生物信号(ECG/MPU/音频/视频)并按BIDS标准组织。0 star/0 fork/0 watcher,仅4次提交,无releases。README明示"latest code can be found in the TTLab official repository",本仓库为论文快照,后续开发已迁至TTLab官方仓库(可能闭源需申请)。判断:与狗知识库主题部分相关——是犬行为研究数据采集工具+论文文档,但本身是空脚手架与采集代码,非已填充的知识库/数

### Liuyangpai (遛养派) 
- URL: https://www.19up.com/about
- 类型: mixed | 子领域: behavior+breed+genetics/neuroscience(犬类行为遗传神经机制为主);整体平台覆盖behavior/breed/care/training/nutrition/general | is_real: partial
- license: 未提及(闭源商业平台,无开源许可;仅有闽ICP备20008564号备案) | 活跃: active | star: N/A(非GitHub仓库,为商业网站) | 更新: v2026.7(首页标注版本,© 2026,当前活跃维护)
- 内容范围: 核心为犬类行为遗传/神经机制知识库:四维加权模型(结构特征表达/神经通路激活/受体功能/基因调控),已追踪25个行为相关基因、17个神经递质受体、18条脑区神经通路、55项结构特征(头面部/运动系统/被毛3大分类×11子分类),覆盖200+犬种,整合Parker 2017/Plassais 2019等公开基因数据及FCI/AKC犬种标准。但整体平台范围更广:429+犬猫品种库(含猫)、1092+问答、86营养库、50代谢指标、44知识文章、4大科学计算器(BMR/宠粮分析/结构分析/食谱分析)、宠物情绪词典(42情绪+18安抚信号)、训练技巧等。即:犬类行为KB真实存在,但嵌入在更大的犬猫混合商业平台中。
- 备注: 核实结论:描述中的全部量化指标(25基因/18脑区通路/17受体/55结构特征/200+品种/四维加权模型/多学科)在/about页均逐字确认,犬类行为知识库内容真实存在,fetch_status=success。

但需对抗核验的三大矛盾:
1.【开放性夸大】/about页宣称"研究方法公开""数据验证过程向社区开放""接受专业社区审查",但首页(/)实际扫描显示:无GitHub链接、无公开数据集下载、无API、无开源许可、无研究方法论页面链接,唯一联系渠道为lyp@19up.com。底层"自建多维度关联数据库"为闭源专有,仅通过网站界面访问。开放承诺与实际不符。

2.【范围不一致】已知描

### Dog Translator Behavior Dictionary (狗语翻译器 - 狗狗行为词典) 
- URL: https://dogtranslator.org/zh/dictionary.html
- 类型: mixed | 子领域: behavior | is_real: partial
- license: insufficient data (非开源项目,页面未声明任何 license) | 活跃: unknown (商业站点,无 commit/版本/release 信息可判断活跃度) | star: N/A (非 GitHub repo,无 star) | 更新: insufficient data (网页无更新日期/版本信息)
- 内容范围: 页面实际列出 10 条狗行为信号词条及简要含义解读:1.快速摇尾(开心/期待;尾根僵硬伴盯视则为紧张) 2.持续吠叫(短促尖锐为警戒,节奏均匀为兴奋/邀玩) 3.低吼(保持距离信号,伴身体僵硬/耳朵后贴) 4.呜咽(焦虑/求关注/不适,观察是否抓门踱步) 5.喘气(运动后正常;室内大力喘气需排查紧张/过热) 6.翻肚子(放松为信任;僵硬伴喘气为安抚信号) 7.耳朵后贴(轻微后贴友好,贴紧头部害怕/紧张) 8.尾巴夹紧(典型压力信号,需给空间) 9.邀玩姿势(前腿伏低臀部抬高,邀玩/礼貌缓冲) 10.舔脸舔手(亲近/安抚/求注意)。内容真实准确,但仅覆盖行为信号解读单一维度,无疾病/品种/饲养/训练系统化内容。页面同时推销"行为工作室""AI深度分析""语音翻译器""品种探索器"等商业产品功能。
- 备注: 核实结论:该 URL 不是开源项目/GitHub repo,而是商业产品"狗语翻译器"(dogtranslator.org)网站中的一个行为参考页面。已知描述"狗狗行为信号词典"在内容层面基本属实——页面确列出 10 条行为信号词条(摇尾/吠叫/低吼/呜咽/喘气/翻肚子/耳朵后贴/尾巴夹紧/邀玩姿势/舔脸舔手),解读准确,与 canine 行为学常识一致。但将其归类为 "doc-kb" 类型有显著偏差:(1) 它是嵌在商业产品营销页里的附属参考内容,非独立知识库/数据集/文档仓库;(2) 无 license、无 star、无 commit 日期、无可下载数据;(3) 页面同时推广"行为工作室/

### daisy-kyushu/daisy-kyushu-dog-guide 
- URL: https://github.com/daisy-kyushu/daisy-kyushu-dog-guide
- 类型: doc-kb | 子领域: general(旅行/生活指南;含 care 护理、breed 萨摩耶犬种、training 礼仪等元素,但非专题知识库) | is_real: partial
- license: 无(未在 README/仓库中指定) | 活跃: active | star: 1 | 更新: 仓库共 303 commits(具体最后提交日期未在页面明确显示)
- 内容范围: 日本九州地区狗狗旅行/生活指南静态网站(GitHub Pages)。内容覆盖:狗友好地点(spots)、宠物友好酒店(hotels)、户外活动、狗跑(dog run)、宠物友好咖啡馆、紧急/医院目录、旅行清单、行程规划、活动列表、夏季中暑护理贴士、萨摩耶犬种相关内容(Daisy 吉祥物)、博客文章(狗狗徒步、海滩旅行、礼仪、季节护理)。文件含 index/spots/hotels/events/checklist/weekend/map/admin 等多 HTML 页,JSON 数据(products/hotels/spots/events.json),DATA_RULES.md 数据规则,GitHub Actions 自动化(乐天产品更新、活动清理、Instagram 草稿生成)。非传统知识库/数据集,而是面向消费者的旅行指南站
- 备注: 描述与实际有出入需对抗核验:已知描述称"萨摩耶犬种专题网站(SamoyedWebサイト)",实际抓取显示为"九州地区狗狗旅行/生活指南网站",萨摩耶犬 Daisy 仅作为品牌吉祥物/QR 形象(daisy_samoyed1217_qr.png),非犬种专题知识库。确与狗相关(is_real_dog_kb=partial),但非传统狗知识库/文档/数据集,而是面向消费者的地区旅行指南静态站。规模小(star=1),个人项目性质,无 license。两次抓取(GitHub 主页 + raw README)信息一致,fetch 成功。判断为非重点对比候选(is_key_candidate=false

### Oxford-IIIT Pet Dataset (VGG) 
- URL: https://www.robots.ox.ac.uk/~vgg/data/pets/
- 类型: dataset | 子领域: breed | is_real: partial
- license: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | 活跃: archived | star: N/A (非GitHub仓库,学术数据集页面) | 更新: insufficient data (页面未注明更新日期;数据集发布于2012 CVPR,属稳定存档学术资源)
- 内容范围: 37类宠物图像数据集(25犬品种+12猫品种),约7400张图片(每类约200张),含大尺度/姿态/光照变化。标注包括:1)品种/物种标签;2)头部ROI(头部紧致边界框);3)像素级trimap前景-背景分割标注。犬品种含Boxer/Beagle/Pug/Chihuahua/Shiba Inu/Saint Bernard/Yorkshire Terrier等;猫品种含Abyssinian/Bengal/Persian/Siamese/Sphynx等。主要用于品种分类识别与图像分割基准。CVPR 2012发表,作者Parkhi/Vedaldi/Zisserman/Jawahar。下载途径:Academic Torrents(BitTorrent)或HTTP,约800MB。
- 备注: WebFetch成功抓取主页完整内容;mcp__fetch__fetch备用被robots.txt阻止(User-agent: * Disallow: /),但主抓取已获充分信息无需备用。已知描述(37品种=25犬+12猫、约7400图、品种标签+头部ROI+trimap分割)与实际页面内容逐项核实完全一致,无营销夸大或矛盾。判断为partial:确为真实知名学术数据集且含25个犬品种,但本质是宠物(猫+狗)图像分类/分割数据集而非专门狗知识库/文档/ontology,内容维度局限于品种外观图像+分割标注,不覆盖行为/疾病/饲养/训练/本体知识。作为对比报告重点候选合适:经典基准数据集,引用率

### dog-ceo-api (Dog CEO API) 
- URL: https://github.com/ElliottLandsborough/dog-ceo-api
- 类型: tool | 子领域: breed | is_real: partial
- license: MIT | 活跃: active | star: 712 | 更新: insufficient data (具体最新提交日期未抓取到; 共632次提交, 依赖为 PHP 8.3+/Symfony 6 现代栈, 暗示持续维护)
- 内容范围: 犬种图片与品种分类REST API。包含: (1)结构化犬种分类数据——/breeds/list/all 返回98个主品种及其子品种层级对象(如 bulldog:[boston,english,french]、hound:[afghan,basset,blood,english,ibizan,plott,walker]、terrier含25个子品种); (2)按品种/子品种的随机图片端点(图片为.jpg格式,托管于images.dog.ceo CDN); (3)品种信息端点——但README明确标注"data is incomplete, see content folder",多数品种返回404 "No info file for this breed exists"。不含行为/疾病/护理/训练/本体内容。图片数据存储于独立伴随仓库 jigsawpieces/dog-api-images,本仓库仅含API代码(PHP/Symfony)。
- 备注: 抓取过程: WebFetch 抓 repo 主页成功(获项目元数据); raw README URL (HEAD/master/main, README.md) 均 404——实际文件名为小写 readme.md; 改用 mcp__fetch__fetch 抓 repo 页成功获得完整 README 内容(含全部端点文档); GitHub API (api.github.com/repos/...) 返回 403 Forbidden。

判断依据: 项目100%犬类专用(非通用宠物),含真实结构化犬种分类数据(98主品种+子品种层级,属breed subdomain真实数据集),但本质是图片A

### artuguen28/PawAid-AI 
- URL: https://github.com/artuguen28/PawAid-AI
- 类型: mixed | 子领域: care (first-aid/emergency/toxicology) | is_real: partial
- license: MIT | 活跃: stale | star: 0 | 更新: 2026-02-01 (pushed_at); created 2026-01-16
- 内容范围: 宠物急救/中毒毒理(宣称 cats & dogs,实际KB为猫专属)。data/chunks.json 仅含 1 份 PDF(cat-poisons-for-cats.pdf, 3页, 7个RAG chunks, ~11KB),内容:猫中毒食物(巧克力/葡萄/洋葱/木糖醇等)、人药警告、宠物中毒热线、有毒植物(~60+种)、家居安全隐患、化学品危害(防冻剂/苯酚类)。狗仅在 chunk0 一句对比中提及(While cats don't beg the same way a dog does),metadata.animal_types 仅 chunk0 标[cat,dog]其余均[cat],无任何狗专属毒理/急救知识。README 自述仍在 Building document ingestion pipeline。无品种/行为/训练/疾病/本体内容。
- 备注: 核实结论:并非狗知识库,实际为猫中毒毒理 RAG 数据集。关键出入:(1)已知描述称"RAG 检索兽医指南知识库",但实际 KB 仅 1 份 3 页猫中毒 PDF(cat-poisons-for-cats.pdf),非通用兽医指南,规模极小;(2)项目宣称 cats & dogs,但 data/chunks.json 中狗仅在一句话对比中出现,无狗专属内容;(3)README 自述"Building document ingestion pipeline",即 RAG 管线仍在搭建,非成熟可用。仓库结构: app/ data/ docs/ scripts/ src/ + .gitignore/

### GuidePaw 
- URL: https://github.com/jphutching/GuidePaw
- 类型: code | 子领域: training | is_real: partial
- license: No license (unlicensed,仓库根无license文件) | 活跃: active | star: 1 | 更新: 2026-07-02
- 内容范围: 服务犬/导盲犬训练管理软件(PHP Web应用 + Kotlin Android companion app + PostgreSQL)。功能含: dog profiles(犬只档案)、training logs with GPS capture(训练日志带GPS)、training history(训练历史)、reports(报告)、breed comparison tools(品种对比)、ADA access cards(ADA通行卡)、behavioral risk scoring(行为风险评分)、health tracking(健康追踪)、community features(社区)、certification tracking(认证追踪)、AI training assistant(AI训练助手)、appointment management(预约管理)、backup(备份)。注意:这是应用代码/工具,非知识库/文档/数据集。
- 备注: 已知描述'doc-kb 服务犬训练网站(PHP)'与实际部分不符:确实围绕服务犬/导盲犬训练,且确为PHP网站,但形态是应用代码/工具(含Android app、Docker、PostgreSQL schema、部署指南),非知识库/文档/数据集。仓库903次提交、1 star、无license、最近提交2026-07-02(活跃开发中)。README明确说明为'PostgreSQL-only GuidePaw package prepared from the latest working build'部署包,警告勿reintroduce MySQL/MariaDB。内容虽涉及训练/行为/品

### VetDataHub 
- URL: https://github.com/Vetdatahub/VetDataHub
- 类型: dataset | 子领域: general (多物种兽医综合目录); 犬部分覆盖 breed(品种分类,3个数据集)、disease(仅犬齿年龄1个,临床病理边缘)、intelligence(品种级智力排名,非个体行为);无 care/training/behavior/ontology | is_real: partial
- license: MIT (仓库根 LICENSE 为 MIT);README 同时声明数据集应无版权限制但未对项目本身命名具体许可证 | 活跃: unknown (21 commits,stars 44,无最近提交日期可判断;目录为静态索引) | star: 44 | 更新: insufficient data (主页仅显示 "21 Commits",无明确日期戳;README/提交时间未在抓取页显示)
- 内容范围: 兽医多物种数据集索引目录（非知识库）。仓库 Datasets/ 目录含 25 个 markdown 分类文件：anatomy/animal_condition/animal_welfare/avian/behavioral/biochemistry/canine/clinical_records/diagnostic_imaging/epidermiology/equine/farm/feline/genetics/immunology/laboratory/microbiology/others/pathology/pharmacology/physiological/rabbit-disorder/research_papers/veterinary_images/wildlife。canine.md 索引 7 个犬相关外部数据集：(1)Dog Teeth Age—44张犬齿影像配年龄标签(Unizg兽医病理系GitHub,唯一临床病理类)；(2)Dog Breed Classification—Kaggle 120品种；(3)DogBreed—Kaggle 133类train/test/val；(4)Dog Parks of NYC—NYC狗公园地理数据；(5)Dogs Intelligence and Size—AKC+Stanley Coren研究品种体型智力；(6)Fit a Dog for me—170+品种特性；(7)Dog Intelligence Comparison Based on Size—Coren研究体型vs智力。无犬疾病数据集、无犬行为观测数据、无护理/训练知识。大部分为 Kaggle 外部链接，非仓库内托管数据。
- 备注: 核实结论：与已知描述存在显著偏差，需对抗核验。已知描述称"开源兽医数据集仓库，涵盖医学影像/临床记录/基因组/流行病学数据，按类型分类存放"——实际是兽医数据集的【外部链接索引目录】，Datasets/ 下 25 个 .md 文件均为分类索引页，指向 Kaggle/GitHub 外部数据集，仓库内并不托管真实 zip/rar 数据归档（尽管 contributing.md 声称数据应以 zip/rar 存放于 datasets 文件夹）。1) 非狗专属知识库：是多物种兽医目录（含 avian/equine/feline/farm/wildlife 等约 12 个物种分类），犬仅为其中一类。2)

### Pet Health Symptoms Dataset (yyzz1010) 
- URL: https://www.kaggle.com/datasets/yyzz1010/pet-health-symptoms-dataset
- 类型: dataset | 子领域: disease | is_real: partial
- license: MIT | 活跃: stale | star: 3 likes (Kaggle无star概念;690 downloads,4463 views,0 comments) | 更新: 2025-04-24 (version 8)
- 内容范围: 2000条LLM合成(Gemini 2.5 Pro)宠物健康症状文本样本，5类病情(Skin Irritations皮肤刺激/Digestive Issues消化问题/Parasites寄生虫/Ear Infections耳部感染/Mobility Problems行动问题)，2种记录类型(主人观察 Owner Observation / 临床记录 Clinical Notes)。字段:text、condition、record_type。任务:文本分类(二分类/多分类/多任务)。用途:宠物健康聊天机器人、分诊系统、兽医教学、保险理赔、EHR结构化。局限:合成数据非真实病历、仅5类病情、物种偏猫狗(少异宠)、无年龄/品种元数据。非狗专属知识库，是猫狗通用的症状文本分类数据集。
- 备注: Kaggle数据集(非GitHub repo)，通过抓取原始HTML中的JSON-LD schema.org元数据获得完整信息，元数据自洽无矛盾。结论:是真实存在的宠物健康症状文本分类数据集，但并非狗专属知识库——为猫狗通用合成NLP数据，无品种/年龄/物种元数据，文本为物种无关的分类样本。规模小(2000条/56KB)，合成数据(Gemini生成)，活跃度低(3 likes/0评论/最后更新2025-04)。不适合作为"狗知识库对比报告"重点，仅可作为宠物健康NLP领域的次要参考点。已知描述"宠物健康症状数据集(含狗疾病症状)"基本准确但需修正:含狗但非狗专属，且为合成数据非真实症状。无需对