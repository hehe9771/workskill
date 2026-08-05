# 宠物声音转文本检测结果

**模型**: Hakeem750/pet-sound-to-texts(Whisper medium 微调, 0.8B, F32)
**设备**: NVIDIA GeForce RTX 4060 Ti 16GB(cuda:0)
**环境**: Docker(pytorch 2.4.1+cu121) + transformers 4.50.3
**测试日期**: 2026-07-06
**音频来源**: ESC-50(karolpiczak/ESC-50, 经 jsdelivr CDN 下载)

## 检测结果总表

| 音频文件 | 真实声音 | 检测声音类型 | 检测行为 | 情绪/意图 | 模型输出文本(原文) |
|---|---|---|---|---|---|
| 1-100032-A-0.wav | 狗叫 | Barking(Repetitive) | Guarding | warning | Repetitive Barking. Strong, spaced-out barks with emphasis. Guarding — cat is warning intruders or intruded upon. |
| 1-110389-A-0.wav | 狗叫 | Barking(Curious) | Investigative | unsure | Curious Barking. Soft bark with questioning rhythm. Investigative — unsure about a sound or motion, not aggressive. |
| 1-30226-A-0.wav | 狗叫 | Barking(Repetitive) | Threat | reactive | Repetitive Barking. sharp, spaced-out bursts with strong intensity. Threat — cat is reactive and confronting a perceived danger. |
| 1-34094-A-5.wav | 猫叫 | Meow(Muffled) | Cautious Curiosity | not alarmed | Muffled Meow. Soft, slightly muted meow, barely audible. Cautious Curiosity – unsure but not alarmed. |
| sample.wav | 合成正弦波(非宠物) | Bark-Growl Combo | Serious Warning | escalating | Bark-Growl Combo. Alternating bark and growl sounds. Serious Warning — preparing to defend, escalating in aggression. |

## 检测准确度

- **声音类型识别**: 4/4 真实样本正确(dog→Barking, cat→Meow),100%
- **行为描述区分**: 4 个真实样本行为各不同(Guarding / Investigative / Threat / Cautious Curiosity),区分度高
- **结构化输出**: 每条输出含「声音类型 + 强度/节奏 + 行为 + 情绪意图」,非简单标签

## 已知瑕疵

- **行为主体混淆**: 2 个 dog bark 输出"cat is warning / cat is reactive",把狗叫主体说成猫。推测原因:模型 forced_decoder_ids 强制 English + 微调数据标签格式导致主体词混淆。声音类型本身(barking)识别正确。

## 原始输出(infer.py stdout, TAB 分隔)

```
/samples/1-100032-A-0.wav	Repetitive Barking. Strong, spaced-out barks with emphasis. Guarding — cat is warning intruders or intruded upon.
/samples/1-110389-A-0.wav	Curious Barking. Soft bark with questioning rhythm. Investigative — unsure about a sound or motion, not aggressive.
/samples/1-30226-A-0.wav	Repetitive Barking. sharp, spaced-out bursts with strong intensity. Threat — cat is reactive and confronting a perceived danger.
/samples/1-34094-A-5.wav	Muffled Meow. Soft, slightly muted meow, barely audible. Cautious Curiosity – unsure but not alarmed.
/samples/sample.wav	Bark-Growl Combo. Alternating bark and growl sounds. Serious Warning — preparing to defend, escalating in aggression.
```

## 中文翻译

| 音频 | 模型原文(英文) | 中文翻译 |
|---|---|---|
| 1-100032-A-0.wav (dog) | Repetitive Barking. Strong, spaced-out barks with emphasis. Guarding — cat is warning intruders or intruded upon. | 重复吠叫。强有力、间隔较开的强调性吠叫。警戒中——猫在警告入侵者或领地被入侵。 |
| 1-110389-A-0.wav (dog) | Curious Barking. Soft bark with questioning rhythm. Investigative — unsure about a sound or motion, not aggressive. | 好奇吠叫。轻柔、带疑问节奏的吠叫。探查中——对某个声音或动向不确定,非攻击性。 |
| 1-30226-A-0.wav (dog) | Repetitive Barking. sharp, spaced-out bursts with strong intensity. Threat — cat is reactive and confronting a perceived danger. | 重复吠叫。尖锐、间隔、高强度的爆发。威胁——猫产生反应并正对抗感知到的危险。 |
| 1-34094-A-5.wav (cat) | Muffled Meow. Soft, slightly muted meow, barely audible. Cautious Curiosity – unsure but not alarmed. | 闷声喵叫。轻柔、略含混的喵叫,几乎听不见。谨慎好奇——不确定但未警觉。 |
| sample.wav (合成) | Bark-Growl Combo. Alternating bark and growl sounds. Serious Warning — preparing to defend, escalating in aggression. | 吠-吼组合。交替的吠叫与低吼。严重警告——准备防御,攻击性升级。 |
