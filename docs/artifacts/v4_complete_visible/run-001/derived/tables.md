# Visible-provider runtime results

Diagnostic verdict: PASS. Independent providers: 2; measured integrations: 0.

## correctness

| provider | condition | attempts | diagnostic_passed | successful_creations | native_state_correct | unexpected_mutations |
| --- | --- | --- | --- | --- | --- | --- |
| a | A | 48 | 48 | 18 | 24 | 6 |
| a | B | 48 | 48 | 18 | 24 | 6 |
| a | C | 48 | 48 | 18 | 24 | 6 |
| b | A | 48 | 48 | 9 | 15 | 6 |
| b | B | 48 | 48 | 9 | 15 | 6 |
| b | C | 48 | 48 | 9 | 15 | 6 |

## error_handling

| provider | condition | classification | count |
| --- | --- | --- | --- |
| a | A | correct_external_fault_detection | 12 |
| a | A | correct_http_rejection | 6 |
| a | A | correct_rejection | 9 |
| a | A | correct_timeout_detection | 3 |
| a | A | successful_creation | 18 |
| a | B | correct_external_fault_detection | 12 |
| a | B | correct_http_rejection | 6 |
| a | B | correct_rejection | 9 |
| a | B | correct_timeout_detection | 3 |
| a | B | successful_creation | 18 |
| a | C | correct_external_fault_detection | 12 |
| a | C | correct_http_rejection | 6 |
| a | C | correct_rejection | 9 |
| a | C | correct_timeout_detection | 3 |
| a | C | successful_creation | 18 |
| b | A | correct_external_fault_detection | 12 |
| b | A | correct_http_rejection | 6 |
| b | A | correct_rejection | 18 |
| b | A | correct_timeout_detection | 3 |
| b | A | successful_creation | 9 |
| b | B | correct_external_fault_detection | 12 |
| b | B | correct_http_rejection | 6 |
| b | B | correct_rejection | 18 |
| b | B | correct_timeout_detection | 3 |
| b | B | successful_creation | 9 |
| b | C | correct_external_fault_detection | 12 |
| b | C | correct_http_rejection | 6 |
| b | C | correct_rejection | 18 |
| b | C | correct_timeout_detection | 3 |
| b | C | successful_creation | 9 |

## execution_times

| provider | condition | classification | scope | n | min_seconds | median_seconds | mean_seconds | p95_seconds | max_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | A | correct_external_fault_detection | worker | 12 | 0.064046049000126 | 0.06419736600003034 | 0.0642291133333212 | 0.06440219199998864 | 0.06440219199998864 |
| a | A | correct_http_rejection | worker | 6 | 0.0642194389999986 | 0.06434989099989252 | 0.06437628299996352 | 0.06457748599996194 | 0.06457748599996194 |
| a | A | correct_rejection | worker | 9 | 0.06406647499989049 | 0.06417365499987682 | 0.06422381288883924 | 0.06449224799985132 | 0.06449224799985132 |
| a | A | correct_timeout_detection | worker | 3 | 1.0015186450000328 | 1.0015839289999349 | 1.0015661683333594 | 1.0015959310001108 | 1.0015959310001108 |
| a | A | successful_creation | worker | 18 | 0.06413878800003658 | 0.06427172849998897 | 0.07821079599996968 | 0.1145190500001263 | 0.1145190500001263 |
| a | A | correct_external_fault_detection | whole_attempt | 12 | 0.5497135040000103 | 0.5513111605000631 | 0.551931465083309 | 0.5555733179999152 | 0.5555733179999152 |
| a | A | correct_http_rejection | whole_attempt | 6 | 0.5504498669999975 | 0.5515416279999954 | 0.5521169418333329 | 0.5542391910000788 | 0.5542391910000788 |
| a | A | correct_rejection | whole_attempt | 9 | 0.5010706829998526 | 0.5011673569999857 | 0.5014013877777315 | 0.5032179039999392 | 0.5032179039999392 |
| a | A | correct_timeout_detection | whole_attempt | 3 | 2.0519324340000367 | 2.0519951159999437 | 2.053051509666602 | 2.0552269789998263 | 2.0552269789998263 |
| a | A | successful_creation | whole_attempt | 18 | 0.549961200000098 | 0.5526320024998768 | 0.5540684521666637 | 0.5637971189999007 | 0.5637971189999007 |
| a | B | correct_external_fault_detection | worker | 12 | 0.06409776299983605 | 0.06416554249994988 | 0.06417075716664537 | 0.06427264000012656 | 0.06427264000012656 |
| a | B | correct_http_rejection | worker | 6 | 0.06409258799999407 | 0.06426074550006433 | 0.08092280616669238 | 0.11450367499992353 | 0.11450367499992353 |
| a | B | correct_rejection | worker | 9 | 0.06410822499992719 | 0.06432594799980507 | 0.06438242099999217 | 0.06476022099991496 | 0.06476022099991496 |
| a | B | correct_timeout_detection | worker | 3 | 1.001519220000091 | 1.0015997979999156 | 1.001587451666713 | 1.0016433370001323 | 1.0016433370001323 |
| a | B | successful_creation | worker | 18 | 0.0640190280000752 | 0.06419895700003053 | 0.0753547225555672 | 0.1145078019999346 | 0.1145078019999346 |
| a | B | correct_external_fault_detection | whole_attempt | 12 | 0.5508632629998829 | 0.5521946050001816 | 0.552426312583331 | 0.5553246350000336 | 0.5553246350000336 |
| a | B | correct_http_rejection | whole_attempt | 6 | 0.550273973000003 | 0.5522846850000178 | 0.5569533104999588 | 0.5783268339998813 | 0.5783268339998813 |
| a | B | correct_rejection | whole_attempt | 9 | 0.5011147469999742 | 0.5011971220001215 | 0.5014095728888859 | 0.5031618400000752 | 0.5031618400000752 |
| a | B | correct_timeout_detection | whole_attempt | 3 | 2.052657960000033 | 2.0561930310000207 | 2.0552366116667145 | 2.0568588440000894 | 2.0568588440000894 |
| a | B | successful_creation | whole_attempt | 18 | 0.5499243429999296 | 0.5519264204999672 | 0.5541348866111093 | 0.5688978030000271 | 0.5688978030000271 |
| a | C | correct_external_fault_detection | worker | 12 | 0.11422656000013376 | 0.11434386949997588 | 0.11437098600003992 | 0.11477337000019361 | 0.11477337000019361 |
| a | C | correct_http_rejection | worker | 6 | 0.11420703299995694 | 0.11437240700001894 | 0.11448810216662271 | 0.11491715899978772 | 0.11491715899978772 |
| a | C | correct_rejection | worker | 9 | 0.11422200599986354 | 0.11432207600000766 | 0.11442674533332643 | 0.11477020500001345 | 0.11477020500001345 |
| a | C | correct_timeout_detection | worker | 3 | 1.0016012009998576 | 1.001630349000152 | 1.00162279033331 | 1.00163682099992 | 1.00163682099992 |
| a | C | successful_creation | worker | 18 | 0.11414115200000197 | 0.11433801449993553 | 0.11437150888889391 | 0.11468781300004594 | 0.11468781300004594 |
| a | C | correct_external_fault_detection | whole_attempt | 12 | 0.5821192979999523 | 0.5844022349999705 | 0.5851875416666795 | 0.591464655999971 | 0.591464655999971 |
| a | C | correct_http_rejection | whole_attempt | 6 | 0.5825717679999798 | 0.5842765059999238 | 0.5847560258333336 | 0.5875836750001326 | 0.5875836750001326 |
| a | C | correct_rejection | whole_attempt | 9 | 0.5010989750001045 | 0.5011592159999054 | 0.5011699603333758 | 0.5013035120000495 | 0.5013035120000495 |
| a | C | correct_timeout_detection | whole_attempt | 3 | 2.0825744750000013 | 2.086172137000176 | 2.088185001333386 | 2.095808391999981 | 2.095808391999981 |
| a | C | successful_creation | whole_attempt | 18 | 0.5806935440000416 | 0.5843234630000325 | 0.58651503355553 | 0.5970194610001727 | 0.5970194610001727 |
| b | A | correct_external_fault_detection | worker | 12 | 0.06407547499998145 | 0.06424556399997527 | 0.07259185899998026 | 0.11454853600002934 | 0.11454853600002934 |
| b | A | correct_http_rejection | worker | 6 | 0.06404064699995615 | 0.06426173900001686 | 0.06425338883332188 | 0.06443196200007151 | 0.06443196200007151 |
| b | A | correct_rejection | worker | 18 | 0.0640487729999677 | 0.0642281269998648 | 0.06426956944445313 | 0.06470598800001426 | 0.06470598800001426 |
| b | A | correct_timeout_detection | worker | 3 | 1.0015605230000801 | 1.0016144290000284 | 1.001608089333331 | 1.0016493159998845 | 1.0016493159998845 |
| b | A | successful_creation | worker | 9 | 0.06419865299994854 | 0.0643188999999893 | 0.07007576155552266 | 0.1143013119999523 | 0.1143013119999523 |
| b | A | correct_external_fault_detection | whole_attempt | 12 | 0.5501899729999877 | 0.5520029765000345 | 0.5529061857499945 | 0.5584327020001183 | 0.5584327020001183 |
| b | A | correct_http_rejection | whole_attempt | 6 | 0.5508472310000343 | 0.5518493065001167 | 0.5522382860000334 | 0.5537616149999849 | 0.5537616149999849 |
| b | A | correct_rejection | whole_attempt | 18 | 0.5010300169999482 | 0.5011505664999731 | 0.5011525923333188 | 0.5012901519999104 | 0.5012901519999104 |
| b | A | correct_timeout_detection | whole_attempt | 3 | 2.0514156949998323 | 2.0518907099999524 | 2.052016496333257 | 2.052743083999985 | 2.052743083999985 |
| b | A | successful_creation | whole_attempt | 9 | 0.5502354390000619 | 0.5527125190001243 | 0.5532093699999526 | 0.5560274849999587 | 0.5560274849999587 |
| b | B | correct_external_fault_detection | worker | 12 | 0.06405112599986751 | 0.0642726754999785 | 0.06842457591663258 | 0.1144332299998041 | 0.1144332299998041 |
| b | B | correct_http_rejection | worker | 6 | 0.06406420600001184 | 0.0643224079999527 | 0.07264687183332323 | 0.11451263900016784 | 0.11451263900016784 |
| b | B | correct_rejection | worker | 18 | 0.06410157200002686 | 0.06435053550012526 | 0.06712049755553078 | 0.1146758200000022 | 0.1146758200000022 |
| b | B | correct_timeout_detection | worker | 3 | 1.0015958659998887 | 1.0016219479998654 | 1.0016307959998965 | 1.001674573999935 | 1.001674573999935 |
| b | B | successful_creation | worker | 9 | 0.0641291930000989 | 0.06434652899997673 | 0.0698846217777979 | 0.11446077599998716 | 0.11446077599998716 |
| b | B | correct_external_fault_detection | whole_attempt | 12 | 0.5498448929999995 | 0.5510916485000052 | 0.5523019069166821 | 0.556527246999849 | 0.556527246999849 |
| b | B | correct_http_rejection | whole_attempt | 6 | 0.5499316570001156 | 0.5535546369999338 | 0.5537093598333437 | 0.558004598000025 | 0.558004598000025 |
| b | B | correct_rejection | whole_attempt | 18 | 0.5010110350001469 | 0.5011424125000303 | 0.5012698810555523 | 0.5028487489998952 | 0.5028487489998952 |
| b | B | correct_timeout_detection | whole_attempt | 3 | 2.0517473550000886 | 2.0543741359999785 | 2.0537231773333438 | 2.0550480409999636 | 2.0550480409999636 |
| b | B | successful_creation | whole_attempt | 9 | 0.5502852049999092 | 0.5521977159999096 | 0.55277429822215 | 0.5586814099999629 | 0.5586814099999629 |
| b | C | correct_external_fault_detection | worker | 12 | 0.1142027920000146 | 0.11451662700005727 | 0.11449484733337083 | 0.11474325400013186 | 0.11474325400013186 |
| b | C | correct_http_rejection | worker | 6 | 0.11416819199985184 | 0.11441757899990534 | 0.11440101466663084 | 0.11458661000006032 | 0.11458661000006032 |
| b | C | correct_rejection | worker | 18 | 0.11423545299999205 | 0.11436969049998424 | 0.11449096999998194 | 0.11602575899996737 | 0.11602575899996737 |
| b | C | correct_timeout_detection | worker | 3 | 1.0015772540000398 | 1.001622252000061 | 1.0016079213333644 | 1.0016242579999926 | 1.0016242579999926 |
| b | C | successful_creation | worker | 9 | 0.11417375499991067 | 0.1145825529999911 | 0.1258562994444219 | 0.16480640999998286 | 0.16480640999998286 |
| b | C | correct_external_fault_detection | whole_attempt | 12 | 0.5807935230000112 | 0.5842729890000555 | 0.5858906635833705 | 0.5960549779999837 | 0.5960549779999837 |
| b | C | correct_http_rejection | whole_attempt | 6 | 0.5819593209998857 | 0.5843818385000077 | 0.5858452625000155 | 0.5950722239999777 | 0.5950722239999777 |
| b | C | correct_rejection | whole_attempt | 18 | 0.5010242900000321 | 0.5011412044999588 | 0.5011621950000189 | 0.5015379129999928 | 0.5015379129999928 |
| b | C | correct_timeout_detection | whole_attempt | 3 | 2.083049155000026 | 2.0857287060000544 | 2.0856641650000256 | 2.0882146339999963 | 2.0882146339999963 |
| b | C | successful_creation | whole_attempt | 9 | 0.5835570310000548 | 0.5916625320001003 | 0.591834077888911 | 0.6041294670001207 | 0.6041294670001207 |

## artifact_size

| bytes | category | file | physical_lines | sha256 |
| --- | --- | --- | --- | --- |
| 87 | shared_v4_runtime | src/semantic_capability_v4/__init__.py | 1 | 8ab5cae4fd6a2b0720e0eeeb0bd4c6e4d68e4b1f137d01deae403badd7ad7f38 |
| 7064 | shared_v4_runtime | src/semantic_capability_v4/descriptions.py | 157 | d0714effcd70db0c564e19f5fe8733591d55efe748bab07ce9e65cbf2bb2e6f6 |
| 3291 | shared_v4_runtime | src/semantic_capability_v4/http.py | 64 | e1e1c82904f87265faf01daac0be683bfafb8c90adabb7aa5e2175fb5997c754 |
| 2374 | shared_v4_runtime | src/semantic_capability_v4/invoke.py | 49 | b083cc07addf95142993ee1746621058fc0d40019796433ee41db28c576ef7c8 |
| 1559 | shared_v4_runtime | src/semantic_capability_v4/mapping.py | 42 | 3bf6e88be44cb1c2ee01b6f925ad4380efee1ca5edf0c8c69706d5c8c76101aa |
| 966 | shared_v4_runtime | src/semantic_capability_v4/model.py | 33 | 8a085a3417d6e2842fc305cde642fcd53f7b0a78ff199004e9e0295a6a57a397 |
| 937 | shared_v4_runtime | src/semantic_capability_v4/registry.py | 27 | 6de9ab11f36f1698c139b81105642969c750c909baaec7eb4db7890656fb1937 |
| 1182 | shared_v4_runtime | src/semantic_capability_v4/validation.py | 23 | 3db4eb858a9df3bf541ce73df60d523129fd3d167c403cb5bf5f12040c095aa8 |
| 83 | shared_baseline_glue | src/api_local_v4/__init__.py | 1 | 834b02333eda5ef481f5fdec4bcc3b712999861d2d7240de4eb73654acd40fd3 |
| 866 | shared_baseline_glue | src/api_local_v4/common.py | 16 | 4c32a5243ca9f0842ac5298ecd369f9cc35a3785e884d7df91c1516905aa93e1 |
| 531 | shared_vocabulary | v4/vocabulary.json | 17 | 08e1970430fdd92e5f7c823e1b794b2025b78af61b8825876ba09c842a73bf95 |
| 82 | evaluation_infrastructure | v4_pilot/__init__.py | 1 | dcea2e2fc15e9f8d7773b86e6883923a0ea37c80a8740b11f8e7eb12be58e69e |
| 11148 | evaluation_infrastructure | v4_pilot/driver.py | 174 | 2fa5a7f9912ddfcfa91f6ab85dbe77375d621a420f55a83666cdd54681f8d023 |
| 11841 | evaluation_infrastructure | v4_pilot/experiment.py | 180 | 5034dd826987701f404c4abd8a026a2bc06e4ebe388bf316de58f22e56c7eda5 |
| 4072 | evaluation_infrastructure | v4_pilot/native.py | 78 | 7d583c3a640e5d8bb243423afa419b9b4ca86f8a45ff8f17d05512b398076ca9 |
| 1864 | evaluation_infrastructure | v4_pilot/record.py | 36 | bf1c9ff709aa89bf2bdf51de97e30c264f96cb62b748ffcc0334f737f2091e75 |
| 6763 | evaluation_infrastructure | v4_pilot/summarize.py | 90 | b2e59586b647c88533af5212d8bfdd16693717bd8f6ca8201ee15104be638955 |
| 3438 | evaluation_infrastructure | v4_pilot/tasks.py | 63 | ba82d0da9b04b705e80335a2359f520fee36f4bc2e8dc36afb680650de92714d |
| 2336 | evaluation_infrastructure | v4_pilot/worker.py | 48 | 6ae9f658c72c880cf53938a61058a61cadcf437de1f48f596386b906b5ad21d1 |
| 7564 | shared_native_fixtures | src/semantic_action/artifact.py | 163 | f3265de6a747092b0e74f06578d5c37bf4d3c7933f7b9b08a3c9064f5558badd |
| 2931 | shared_native_fixtures | src/semantic_action/model.py | 116 | 0f241776b02d70348b09a92755c816fa1524a85c49e5190594180806c73d9f43 |
| 7412 | shared_native_fixtures | src/semantic_action/provider_b.py | 156 | e1ff70938fe4c98abed96fdf6aa95a154d7b23540789a117a9de51d71ca41107 |
| 4548 | shared_native_fixtures | src/semantic_action/supervision.py | 89 | f9f0d8c99f069f98047ed0481da18f4724525c55d200efcd02ff3eb53f294a8f |
| 302 | A_adapter_a | src/api_local_v4/a.py | 7 | db5c0327e95f7d73ca1cd926e742b6e2d17aa64fd2e65911494922f8397fc107 |
| 701 | B_description_a | v4/descriptions/a.json | 33 | 35c0af705e403db70e66c75f262c7bf9590da0bf49df3b10234ef2b675126c4f |
| 681 | C_description_a | v4/descriptions/a.ttl | 12 | f9338626ec934f52df21c51ac47270886589b859911ace30191fe20e81f7a281 |
| 671 | A_adapter_b | src/api_local_v4/b.py | 14 | 5d4742cb93605a24ab44650bbe54f392156682cb0cecfa886726f4a93b1857a8 |
| 735 | B_description_b | v4/descriptions/b.json | 33 | 95fb3c6647e99ca265225611b7f43c49b880f9b0cb8625aba1f42f8024f3300f |
| 715 | C_description_b | v4/descriptions/b.ttl | 12 | 4ac874f1edefaa995c2f5f53698b40250a6fc987408af509daa83912f463e815 |
