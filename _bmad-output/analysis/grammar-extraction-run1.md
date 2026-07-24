# Grammar-point extraction run

Model: `gpt-5.5` · sentences: 31 · sequential, bank grown per sentence

## #1 (polite)

> 日本人との会話って一年ぶりなんですけど
>
> It's actually been a year since I've had a conversation with a Japanese person…

*Extracted 〜との as the noun-modifying “with/involving” pattern rather than basic と alone. Treated って as casual topic, ぶり as the elapsed-time construction, なんです as explanatory 〜んです, and sentence-final けど as a softening/but ending. Skipped basic は/が/を-style particles since none appear as notable points.*

- `〜との` **NEW** — with; involving · 「日本人との」
- `〜って` **NEW** — casual topic marker · 「会話って」
- `〜ぶり` **NEW** — first time in · 「一年ぶり」
- `〜んです` **NEW** — explanatory tone · 「なんです」
- `〜けど` **NEW** — but; softener · 「けど」

## #2 (polite)

> ただ趣味なんですけど
>
> It's just a hobby, though…

*Reused existing keys for なんです and sentence-final けど. Skipped ただ as a plain adverb meaning “just,” and skipped basic copula/politeness as trivial.*

- `〜んです` — explanatory tone · 「なんです」
- `〜けど` — but; softener · 「けど」

## #3 (polite)

> 旅行で好きなところは、新しい人と出会ったり、日本に住んでいる友達に会ったりできることです。
>
> What I like about traveling is meeting new people and seeing friends who live in Japan.

*Reused no existing bank items. Skipped basic particles like は, で, と, に as ordinary case/topic marking. Treated できる as part of the nominalized clause rather than a separate potential-form grammar point because it is the verb できる here, not a conjugated potential form.*

- `〜ところ` **NEW** — point; aspect · 「ところ」
- `〜たり〜たりする` **NEW** — do things like · 「出会ったり、日本に住んでいる友達に会ったり」
- `〜ている` **NEW** — ongoing state or action · 「住んでいる」
- `〜こと` **NEW** — nominalizes a clause · 「できること」

## #4 (polite)

> 特に日本については、文化がすごく好きです。
>
> In particular, when it comes to Japan, I really like the culture.

*Extracted 〜について as the learner-relevant compound particle meaning “about/regarding”; the following は is just topic/contrast marking attached to it. Skipped basic が and です/politeness as trivial.*

- `〜について` **NEW** — about; regarding · 「日本については」

## #5 (casual)

> 文化って言っても、食べ物とか、習慣とか、アートとか、あとアニメやゲームとか、いろいろあるよね。
>
> When I say culture, I mean all kinds of things, you know — food, customs, art, and also anime and games and stuff.

*Counted 文化って as the existing casual って (quotative/topic-like here) and also the larger set construction 〜と言っても. Extracted とか and や as non-exhaustive listing patterns, and よね as a sentence-ending shared-understanding marker. Skipped plain vocabulary and basic particles.*

- `〜って` — casual quote/topic marker · 「文化って」
- `〜と言っても` **NEW** — although called; even saying · 「文化って言っても」
- `〜とか` **NEW** — things like; etc. · 「食べ物とか、習慣とか、アートとか」
- `〜や` **NEW** — and; among others · 「アニメやゲーム」
- `〜よね` **NEW** — you know; right? · 「あるよね」

## #6 (casual)

> 日本語は全然大丈夫って言いたいんだけど、たまに分からない時があって…
>
> I would like to say japanese is perfectly fine, but there are times i dont understand

*Reused 〜って for the casual quotation use before 言いたい, even though the bank gloss says topic marker. Split んだけど into the existing explanatory 〜んです and softening/contrastive 〜けど. Skipped basic particles は/が and the plain te-form in あって as too general here.*

- `〜って` — casual quotation · 「大丈夫って言いたい」
- `〜たい` **NEW** — want to do · 「言いたい」
- `〜んです` — explanatory tone · 「んだ」
- `〜けど` — but; softener · 「けど」
- `〜時` **NEW** — when; times when · 「分からない時」

## #7 (polite)

> 前回旅行した時、カナダにいる姉に会いに行きました。
>
> Last time I travelled, I visited my sister in canada

*Reused existing 〜時 for 旅行した時. Extracted 会いに行く as the purpose-of-movement に construction. Treated カナダにいる姉 as clause/noun modification. Skipped basic に usages for location/person and plain politeness/past form.*

- `〜時` — when; at the time · 「旅行した時」
- `〜に行く` **NEW** — go to do · 「会いに行きました」
- `〜名詞修飾` **NEW** — clause modifying a noun · 「カナダにいる姉」

## #8 (casual)

> 留学中にDJを覚えて、何回か実際にライブもやったんだけど、オランダに帰ってきてからは一度もやってないんだよね。
>
> I learned to DJ during my exchange and even did some in-person performances, but since coming back to the Netherlands I haven't done a single live event.

*Reused 〜んです for casual んだ, which appears in both やったんだけど and ないんだよね; listed once. Reused 〜ている for the casual negative contraction やってない＝やっていない. Treated 一度も〜ない as a separate negative-polarity construction from ordinary も. Skipped basic case particles and the simple connective て as too trivial here.*

- `〜中に` **NEW** — during; while in · 「留学中に」
- `疑問詞＋か` **NEW** — some; several · 「何回か」
- `〜も` **NEW** — also; even · 「ライブも」
- `〜んです` — explanatory tone · 「やったんだ」
- `〜けど` — but; softener · 「けど」
- `〜てくる` **NEW** — come to; become · 「帰ってきて」
- `〜てから` **NEW** — after doing · 「帰ってきてから」
- `〜も〜ない` **NEW** — not even; no · 「一度もやってない」
- `〜ている` — ongoing state or action · 「やってない」
- `〜よね` — you know; right? · 「よね」

## #9 (casual)

> うちで猟犬を二匹飼っててね、実家にいるんだ。
>
> We have two hunting dogs — they're at my family home (my dad's place).

*Merged contracted 飼ってて（飼っていて） into existing 〜ている. Reused 〜んです for casual んだ. Skipped default particles で・を・に and the counter 二匹 as not target grammar points.*

- `〜ている` — ongoing state or action · 「飼ってて」
- `〜ね` **NEW** — seeking agreement; softener · 「ね」
- `〜んです` — explanatory tone · 「んだ」

## #11 (casual)

> 最近またピアノを始めてね。何曲か覚えたんだけど、今は音楽理論を勉強してるんだ。ちょっと無茶な目標かもだけど、ピアノの前に座って一時間ぶっ通しで即興で弾けるようになりたいんだよね。
>
> I recently started picking up piano again. I learned a few songs, but now I'm studying music theory. It might be a bit of a crazy goal, but I want to be able to sit at a piano and improvise for a solid hour straight.

*Reused bank keys for contractions and combinations: してる → 〜ている, んだ → 〜んです, and んだよね was split into existing 〜んです + 〜よね rather than minted as a duplicate. Skipped basic case particles like を/は/に/で and lexical items such as ぶっ通し.*

- `〜ね` — agreement-seeking softener · 「ね」
- `疑問詞＋か` — some; several · 「何曲か」
- `〜んです` — explanatory tone · 「んだ」
- `〜けど` — but; softener · 「けど」
- `〜ている` — ongoing action · 「してる」
- `〜かも` **NEW** — might; maybe · 「かも」
- `〜て` **NEW** — and; then · 「座って」
- `可能形` **NEW** — can do · 「弾ける」
- `〜ようになる` **NEW** — come to; become able · 「ようになり」
- `〜たい` — want to do · 「たい」
- `〜よね` — right; you know · 「よね」

## #12 (casual)

> 父が獲物を狩るのに使ってて、キジとか鴨とか、季節によって色々。犬は主に回収用なんだ。
>
> My dad uses them to hunt whatever's in season — pheasant, duck, etc. The dogs are mainly for retrieving.

*Reused 〜ている for the contracted 使ってて (=使っていて) and reused 〜んです for casual なんだ. Included the final て in 使ってて、 as conjunctive 〜て. Skipped basic が/を/は and ordinary に usages.*

- `〜のに` **NEW** — for doing; in order to · 「狩るのに」
- `〜ている` — ongoing state or action · 「使ってて」
- `〜て` — and; then · 「使ってて、」
- `〜とか` — things like; etc. · 「キジとか鴨とか」
- `〜によって` **NEW** — depending on · 「季節によって」
- `〜用` **NEW** — for use; for purpose · 「回収用」
- `〜んです` — explanatory tone · 「なんだ」

## #13 (casual)

> 英語が話せない日本人が好きなんだよね。だって、そうなると日本語で話すしかないから。
>
> I like Japanese people who can't speak English, you know? 'Cause then I've got no choice but to speak Japanese.

*Reused bank keys for potential 話せない, noun modification before 日本人, explanatory なんだ, and sentence-ending よね. Treated だって as the standalone causal conjunction, distinct from the bank’s 〜って casual topic marker. Skipped basic が particles and lexical なる/好き as trivial.*

- `可能形` — can do · 「話せない」
- `〜名詞修飾` — clause modifies noun · 「英語が話せない日本人」
- `〜んです` — explanatory tone · 「なんだ」
- `〜よね` — right? you know · 「よね」
- `だって` **NEW** — because; after all · 「だって」
- `〜と` **NEW** — if; when; then · 「そうなると」
- `〜で` **NEW** — by; using; in · 「日本語で」
- `〜しかない` **NEW** — nothing but; no choice · 「話すしかない」
- `〜から` **NEW** — because; since · 「から」

## #14 (casual)

> 留学中に名大のAAR DJクラブでDJのやり方を教えてもらったんだけど、誰かにもっと聴きたいって言われた時、嬉しくなったんだよね。
>
> During my exchange I learned how to DJ at Nagoya University's AAR DJ club, and when someone said they wanted to hear me DJ more, I got happy.

*Split んだけど / んだよね into existing 〜んです plus 〜けど / 〜よね. Treated って as the existing casual quote/topic marker. Skipped basic の・を・に particles and did not separately tag generic noun modification because 言われた時 is covered by 〜時.*

- `〜中に` — during; while in · 「留学中に」
- `〜で` — at; in; by means of · 「クラブで」
- `〜方` **NEW** — way of doing · 「やり方」
- `〜てもらう` **NEW** — receive someone’s doing · 「教えてもらった」
- `〜んです` — explanatory tone · 「もらったんだ」
- `〜けど` — but; softener · 「けど」
- `疑問詞＋か` — someone; something; some · 「誰か」
- `〜たい` — want to do · 「聴きたい」
- `〜って` — casual quotation · 「聴きたいって」
- `受身形` **NEW** — passive voice · 「言われた」
- `〜時` — when; at the time · 「言われた時」
- `〜くなる` **NEW** — become adjective · 「嬉しくなった」
- `〜よね` — right?; you know · 「よね」

## #15 (casual)

> 帰国してから、日本語を話す機会がかなり減っちゃったんだよね。たまにはあるんだけど。
>
> Since coming back home, my chances to speak Japanese have dropped off a lot. I still get them here and there, though.

*Treated 減っちゃった as the casual contraction of 〜てしまう and created the dictionary-style key 〜ちゃう. Reused 〜んです for casual んだ/んだけど. Did not separately tag 〜て inside 〜てから, and skipped basic particles like を/が/は.*

- `〜てから` — after doing · 「帰国してから」
- `〜名詞修飾` — clause modifies noun · 「日本語を話す機会」
- `〜ちゃう` **NEW** — completion; regret · 「減っちゃった」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — right; you know · 「だよね」
- `〜けど` — but; softener · 「んだけど」

## #16 (casual)

> 実家に帰ったら猟犬に会えるし、久しぶりだから早く会いたいんだよね。
>
> If I go back to my parents' place I can see the hunting dogs, and it's been a while so I really want to see them soon.

*Reused 〜んです for plain んだ, and 〜から for だから. Skipped basic に particles and plain だ/ます-level politeness as trivial.*

- `〜たら` **NEW** — if; when · 「帰ったら」
- `可能形` — can do · 「会える」
- `〜し` **NEW** — and; because · 「し」
- `〜ぶり` — first time in · 「久しぶり」
- `〜から` — because; since · 「だから」
- `〜たい` — want to do · 「会いたい」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — you know; right? · 「よね」

## #17 (mixed)

> オランダ人なんだけど…本当は、母語はオランダ語じゃなくて、英語なんですよ。というのも、シンガポール生まれで。
>
> I'm Dutch, but the truth is my first language isn't Dutch — it's English! That's because I was born in Singapore.

*Reused 〜んです for both casual なんだ and polite なんです; listed both occurrences because they appear in different clauses. Treated じゃなくて as the specific negative contrast construction, not just generic 〜て. Skipped basic は and copula/politeness; also skipped the final 生まれで as an elliptical copular connective rather than a distinct tracked point here.*

- `〜んです` — explanatory tone · 「なんだ」
- `〜けど` — but; softener · 「けど」
- `〜じゃなくて/ではなくて` **NEW** — not; rather than · 「じゃなくて」
- `〜んです` — explanatory tone · 「なんです」
- `〜よ` **NEW** — asserting new information · 「よ」
- `〜というのも` **NEW** — the reason is · 「というのも」

## #18 (polite)

> あ、「昨日行った」じゃなくて、「明日行く」という意味でした。
>
> Ah, I meant "I'll go tomorrow," not "I went yesterday."

*Treated じゃなくて as the existing correction/contrast pattern, not a separate 〜て. Extracted 〜という for the quoted content modifying 意味. Skipped plain past/nonpast forms and でした as trivial tense/politeness.*

- `〜じゃなくて/ではなくて` — not; rather than · 「じゃなくて」
- `〜という` **NEW** — called; meaning that · 「「明日行く」という意味」

## #19 (polite)

> 「安い」じゃなくて、「高い」と言いたかったんです。
>
> What I wanted to say was "it's expensive," not "it's cheap."

*Reused existing keys for じゃなくて, たい, and んです. Treated quotative と before 言う as a separate quoting point, not the bank’s conditional 〜と and not the called/meaning 〜という. Skipped basic punctuation/quoted adjectives and the connective て inside じゃなくて as part of that construction.*

- `〜じゃなくて/ではなくて` — not; rather than · 「じゃなくて」
- `〜と（引用）` **NEW** — quoting; that · 「「高い」と」
- `〜たい` — want to do · 「言いたかった」
- `〜んです` — explanatory tone · 「んです」

## #20 (casual)

> 初めてのライブは名大祭でさ、30分で30曲のドラムンベースをかけたんだけど、終わった後もうくたくたになっちゃった。
>
> My first live set was at the Meidai festival — I played 30 drum'n'bass tracks in 30 minutes, and by the end I was completely wrecked.

*Treated 名大祭で as the continuative/copular で corresponding to existing 〜て, while 30分で is the particle で indicating an amount of time. Reused 〜んです for casual んだ and 〜ちゃう for past ちゃった. Treated 〜た後 as distinct from existing 〜てから. Skipped basic は/を/の, past tense, and vocabulary like 初めて/もう.*

- `〜て` — and; then · 「名大祭で」
- `〜さ` **NEW** — you know; softener · 「さ」
- `〜で` — in; within · 「30分で」
- `〜んです` — explanatory tone · 「かけたんだ」
- `〜けど` — but; softener · 「けど」
- `〜た後` **NEW** — after doing · 「終わった後」
- `〜になる` **NEW** — become · 「くたくたになっちゃった」
- `〜ちゃう` — completion; regret · 「なっちゃった」

## #21 (casual)

> DJを始めた頃、自分なりに「DJって2種類いるのかな」ってなんとなく思っててさ。一つは長い曲をかけて、その分ステージでの存在感で見せるタイプ。もう一つは、次々曲を繋いで、とにかく手を動かし続けるタイプなんだよね。
>
> When I started DJing, I sort of had this idea of my own that there might be two types of DJ. One plays long tracks and, to make up for that, carries it with stage presence. The other keeps linking track after track and just constantly keeps their hands moving.

*Treated DJって as the existing casual topic marker, while the later quote-marking って was merged with the bank’s 〜と（引用）. Reused 〜ている for the contraction 思ってて and 〜んです for casual なんだ. Skipped default は/を/に particles, plain verb forms, and vocabulary/adverbial items like なんとなく, 次々, とにかく, その分.*

- `〜頃` **NEW** — around the time when · 「始めた頃」
- `〜なりに` **NEW** — in one’s own way · 「自分なりに」
- `〜って` — casual topic marker · 「DJって」
- `〜のかな` **NEW** — I wonder whether · 「いるのかな」
- `〜と（引用）` — quoting; that · 「「DJって2種類いるのかな」って」
- `〜ている` — ongoing state or action · 「思ってて」
- `〜さ` — you know; softener · 「さ」
- `〜て` — and; then · 「かけて」
- `〜で` — by; using; in · 「存在感で」
- `〜名詞修飾` — clause modifying a noun · 「見せるタイプ」
- `〜続ける` **NEW** — continue doing · 「動かし続ける」
- `〜んです` — explanatory tone · 「なんだ」
- `〜よね` — you know; right? · 「よね」

## #22 (casual)

> で、俺は最初から完全に後者でさ。初ライブの時は絶対に手を止めたくなかったから、あらかじめ30分で30曲やるって決めてたんだよね。とにかく自分を忙しくさせとこう、みたいな感じで。
>
> So from the start I was totally the second type. For my first set I really didn't want to stop moving my hands, so I'd decided in advance to do 30 tracks in 30 minutes. Kind of a "just keep myself busy no matter what" thing.

*Reused 〜と（引用） for casual quotative って, and 〜んです for plain んだ. Treated させとこう as causative + contracted 〜ておく + volitional. Skipped basic は/を/に, source-use 最初から, and discourse/copular で except the time-span 30分で.*

- `〜さ` — you know; softener · 「でさ」
- `〜時` — when; at the time · 「の時」
- `〜たい` — want to do · 「止めたくなかった」
- `〜から` — because; since · 「なかったから」
- `〜で` — in; within; by · 「30分で」
- `〜と（引用）` — quoting; that · 「やるって」
- `〜ている` — resulting state · 「決めてた」
- `〜んです` — explanatory tone · 「たんだ」
- `〜よね` — right?; you know · 「よね」
- `使役形` **NEW** — make/let do · 「忙しくさせ」
- `〜とく/〜ておく` **NEW** — do/leave in advance · 「させとこう」
- `意向形` **NEW** — let’s; will do · 「とこう」
- `〜みたい` **NEW** — like; resembling · 「みたいな」

## #23 (casual)

> 2回目は「ミライノトビラ」っていうパーティーでさ。そこではどうしても自分の作った曲とか、友達の曲をかけたくて、半分が自分ので、もう半分が友達の、みたいな感じだったんだよね。
>
> My second set was at a party called Mirai no Tobira. For that one I really wanted to play tracks I'd made and my friend's tracks, so it was like half mine and half his.

*Merged casual っていう with existing 〜という. Treated かけたくて as both 〜たい and connective/reason 〜て. Skipped basic は・が・を, location で in パーティーで, and possessive/ellipsis の as too trivial here.*

- `〜という` — called; meaning that · 「っていう」
- `〜さ` — you know; softener · 「さ」
- `〜名詞修飾` — clause modifying a noun · 「自分の作った曲」
- `〜とか` — things like; etc. · 「曲とか」
- `〜たい` — want to do · 「かけたくて」
- `〜て` — and; so · 「かけたくて」
- `〜みたい` — like; resembling · 「みたいな」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — you know; right? · 「よね」

## #24 (casual)

> ドラムンベースって曲の構成がわりと一定だから、ずっと途切れなく次から次へと繋いでいけるんだよね。でも今回の曲はちょっと展開が変わってて、決まったところでしか繋げなくてさ。そのおかげで、テーブルにかじりつかなくていい「間」が自然にできたんだ。で、その余裕があったから、初めてちゃんとステージでの見せ方を試せて、ドロップの後のキックロールに合わせて動きながらフロアを煽ったりできたんだよね。
>
> With drum'n'bass the track structure is fairly consistent, so you can keep mixing one track into the next non-stop without any breaks. But the tracks this time had more unconventional arrangements, so you could only mix them at certain points — and thanks to that, natural gaps opened up where I didn't have to be glued to the table. And because I had that breathing room, I could properly try stage presence for the first time — moving in time with the kick rolls after the drop, and working the floor.

*Merged casual んだ into the existing 〜んです key, treated よね separately, treated contracted 変わってて as 〜ている, reused 〜しかない for しか＋negative, and reused 〜たり〜たりする for the single-たり example. Skipped basic は/が/を/に/の uses, locative で in ステージでの, noun の後, and lexical/set expressions like 次から次へと and 途切れなく.*

- `〜って` — casual topic marker · 「ドラムンベースって」
- `〜から` — because; since · 「一定だから」
- `〜ていく` **NEW** — continue doing onward · 「繋いでいける」
- `可能形` — can do · 「試せて」
- `〜んです` — explanatory tone · 「いけるんだ」
- `〜よね` — right? you know? · 「いけるんだよね」
- `〜ている` — ongoing state or action · 「変わってて」
- `〜ところ` — point; stage · 「決まったところ」
- `〜しかない` — only; nothing but · 「でしか繋げなくて」
- `〜さ` — softener; you know · 「繋げなくてさ」
- `〜おかげで` **NEW** — thanks to · 「そのおかげで」
- `〜なくていい` **NEW** — don’t have to · 「かじりつかなくていい」
- `〜名詞修飾` — clause modifies noun · 「かじりつかなくていい「間」」
- `〜方` — way of doing · 「見せ方」
- `〜て` — and; then · 「試せて」
- `〜に合わせて` **NEW** — in accordance with · 「キックロールに合わせて」
- `〜ながら` **NEW** — while doing · 「動きながら」
- `〜たり〜たりする` — do things like · 「煽ったりできた」

## #25 (casual)

> 日本に行く前に、シャドーイングとポッドキャストで耳を慣れさせとこうと思って。
>
> Before the trip to Japan, I figured I'd get my ears reacclimated with shadowing and podcasts.

*Skipped 日本に行く as ordinary destination に＋行く, not the purpose pattern 〜に行く. Skipped noun-linking と as basic coordination. Treated させとこう as contracted させておこう, so reused 〜とく/〜ておく and also tagged the volitional 意向形. Did not separately tag 〜名詞修飾 for 行く前 because it is covered by the more specific 〜前に.*

- `〜前に` **NEW** — before doing · 「行く前に」
- `〜で` — by; using; with · 「シャドーイングとポッドキャストで」
- `使役形` — make; let do · 「慣れさせ」
- `〜とく/〜ておく` — do in advance · 「させとこう」
- `意向形` — will do; let's do · 「とこう」
- `〜と思う` **NEW** — think; intend to · 「と思って」

## #26 (casual)

> 本番前に、DJセット組んどくね。
>
> I'll put my DJ set together before the show.

*Treated 組んどく as the casual contraction of 組んでおく and reused 〜とく/〜ておく. Reused 〜前に for the noun-based 本番前に. Skipped omitted を and other basic particles as trivial.*

- `〜前に` — before doing; before · 「本番前に」
- `〜とく/〜ておく` — do in advance · 「組んどく」
- `〜ね` — softener; seeking agreement · 「ね」

## #27 (casual)

> 今年は毎日ピアノを練習するって決めてたんだよね。
>
> I'd decided I'd practice piano every day this year.

*Treated って as the casual quotative equivalent of 〜と（引用）, not the topic-marker 〜って. Treated 決めてた as contracted 決めていた under 〜ている. Skipped basic は/を, adverbs, vocabulary, and plain form as trivial.*

- `〜と（引用）` — quoting; that · 「って」
- `〜ている` — ongoing state or action · 「決めてた」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — you know; right? · 「よね」

## #28 (casual)

> Uberもう応募した?
>
> Have you applied to Uber yet?

*Treated もう with past tense in a question as the learner-relevant pattern “already/yet.” Skipped Uber/応募 as vocabulary and did not tag plain past した or the bare question intonation as standalone grammar points.*

- `もう〜た` **NEW** — already; yet · 「もう応募した」

## #29 (casual)

> シャドーイングで英語がわかりやすくなっちゃうかも！是非是非やってみて！
>
> With shadowing, english might just start to make more sense! Definitely give it a try!

*Reused bank entries for で as means, 〜くなる, 〜ちゃう, and 〜かも. Added 〜やすい for “easy to understand” and 〜てみる for “try doing.” Skipped が as a basic subject particle and treated the final て in やってみて as part of the 〜てみる request rather than a separate point.*

- `〜で` — by; using; with · 「シャドーイングで」
- `〜やすい` **NEW** — easy to do · 「わかりやすく」
- `〜くなる` — become adjective · 「やすくなっ」
- `〜ちゃう` — end up doing · 「なっちゃう」
- `〜かも` — might; maybe · 「かも」
- `〜てみる` **NEW** — try doing · 「やってみて」

## #30 (casual)

> 人によって意見が違うんだよね。
>
> Opinions differ depending on the person, right?

*Reused 〜によって for the depending-on construction. Merged casual んだ with bank key 〜んです. Treated よね as the combined sentence-ending pattern rather than separate よ and ね. Skipped は/が-style basic particles and vocabulary as trivial.*

- `〜によって` — depending on · 「によって」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — right?; shared understanding · 「よね」

## #31 (casual)

> ジャンルによる曲の繋ぎ方の違いが面白いんだよね。
>
> The differences in how you mix tracks depending on the genre are really interesting.

*Merged による with the existing 〜によって key as the same “depending on/by” pattern. Treated んだ as the casual form of existing 〜んです. Skipped basic が and の particles.*

- `〜によって` — depending on · 「ジャンルによる」
- `〜方` — way of doing · 「繋ぎ方」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — you know; right? · 「よね」

## #32 (casual)

> 曲による難しさの違いが面白いんだよね。
>
> The difference in difficulty depending on the song is really interesting.

*Reused the bank key 〜によって for the synonymous/attributive form による. Split んだよね into explanatory んだ and sentence-final よね. Skipped basic が and の as default particles.*

- `〜によって` — depending on · 「による」
- `〜さ` **NEW** — -ness; degree of · 「難しさ」
- `〜んです` — explanatory tone · 「んだ」
- `〜よね` — you know; right? · 「よね」

---

# Final bank (70 points)

| key | meaning | sentences |
|---|---|---|
| `〜んです` | explanatory tone | #1, #2, #6, #8, #9, #11, #12, #13, #14, #15, #16, #17, #17, #19, #20, #21, #22, #23, #24, #27, #30, #31, #32 |
| `〜よね` | you know; right? | #5, #8, #11, #13, #14, #15, #16, #21, #22, #23, #24, #27, #30, #31, #32 |
| `〜けど` | but; softener | #1, #2, #6, #8, #11, #14, #15, #17, #20 |
| `〜ている` | ongoing state or action | #3, #8, #9, #11, #12, #21, #22, #24, #27 |
| `〜たい` | want to do | #6, #11, #14, #16, #19, #22, #23 |
| `〜で` | by; using; in | #13, #14, #20, #21, #22, #25, #29 |
| `〜って` | casual topic marker | #1, #5, #6, #14, #21, #24 |
| `〜名詞修飾` | clause modifying a noun | #7, #13, #15, #21, #23, #24 |
| `〜て` | and; then | #11, #12, #20, #21, #23, #24 |
| `〜さ` | you know; softener | #20, #21, #22, #23, #24, #32 |
| `〜時` | when; times when | #6, #7, #14, #22 |
| `可能形` | can do | #11, #13, #16, #24 |
| `〜によって` | depending on | #12, #30, #31, #32 |
| `〜から` | because; since | #13, #16, #22, #24 |
| `〜と（引用）` | quoting; that | #19, #21, #22, #27 |
| `〜とか` | things like; etc. | #5, #12, #23 |
| `疑問詞＋か` | some; several | #8, #11, #14 |
| `〜ね` | seeking agreement; softener | #9, #11, #26 |
| `〜方` | way of doing | #14, #24, #31 |
| `〜ちゃう` | completion; regret | #15, #20, #29 |
| `〜じゃなくて/ではなくて` | not; rather than | #17, #18, #19 |
| `〜とく/〜ておく` | do/leave in advance | #22, #25, #26 |
| `〜ぶり` | first time in | #1, #16 |
| `〜ところ` | point; aspect | #3, #24 |
| `〜たり〜たりする` | do things like | #3, #24 |
| `〜中に` | during; while in | #8, #14 |
| `〜てから` | after doing | #8, #15 |
| `〜かも` | might; maybe | #11, #29 |
| `〜しかない` | nothing but; no choice | #13, #24 |
| `〜くなる` | become adjective | #14, #29 |
| `〜という` | called; meaning that | #18, #23 |
| `使役形` | make/let do | #22, #25 |
| `意向形` | let’s; will do | #22, #25 |
| `〜みたい` | like; resembling | #22, #23 |
| `〜前に` | before doing | #25, #26 |
| `〜との` | with; involving | #1 |
| `〜こと` | nominalizes a clause | #3 |
| `〜について` | about; regarding | #4 |
| `〜と言っても` | although called; even saying | #5 |
| `〜や` | and; among others | #5 |
| `〜に行く` | go to do | #7 |
| `〜も` | also; even | #8 |
| `〜てくる` | come to; become | #8 |
| `〜も〜ない` | not even; no | #8 |
| `〜ようになる` | come to; become able | #11 |
| `〜のに` | for doing; in order to | #12 |
| `〜用` | for use; for purpose | #12 |
| `だって` | because; after all | #13 |
| `〜と` | if; when; then | #13 |
| `〜てもらう` | receive someone’s doing | #14 |
| `受身形` | passive voice | #14 |
| `〜たら` | if; when | #16 |
| `〜し` | and; because | #16 |
| `〜よ` | asserting new information | #17 |
| `〜というのも` | the reason is | #17 |
| `〜た後` | after doing | #20 |
| `〜になる` | become | #20 |
| `〜頃` | around the time when | #21 |
| `〜なりに` | in one’s own way | #21 |
| `〜のかな` | I wonder whether | #21 |
| `〜続ける` | continue doing | #21 |
| `〜ていく` | continue doing onward | #24 |
| `〜おかげで` | thanks to | #24 |
| `〜なくていい` | don’t have to | #24 |
| `〜に合わせて` | in accordance with | #24 |
| `〜ながら` | while doing | #24 |
| `〜と思う` | think; intend to | #25 |
| `もう〜た` | already; yet | #28 |
| `〜やすい` | easy to do | #29 |
| `〜てみる` | try doing | #29 |
