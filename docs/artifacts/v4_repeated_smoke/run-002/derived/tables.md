# Visible-provider runtime results

Diagnostic verdict: PASS. Independent providers: 2; measured integrations: 0.

## correctness

| provider | condition | attempts | diagnostic_passed | successful_creations | native_state_correct | unexpected_mutations |
| --- | --- | --- | --- | --- | --- | --- |
| a | A | 8 | 8 | 2 | 4 | 2 |
| a | B | 8 | 8 | 2 | 4 | 2 |
| a | C | 8 | 8 | 2 | 4 | 2 |
| b | A | 8 | 8 | 2 | 4 | 2 |
| b | B | 8 | 8 | 2 | 4 | 2 |
| b | C | 8 | 8 | 2 | 4 | 2 |

## error_handling

| provider | condition | classification | count |
| --- | --- | --- | --- |
| a | A | correct_external_fault_detection | 2 |
| a | A | correct_rejection | 2 |
| a | A | correct_timeout_detection | 2 |
| a | A | successful_creation | 2 |
| a | B | correct_external_fault_detection | 2 |
| a | B | correct_rejection | 2 |
| a | B | correct_timeout_detection | 2 |
| a | B | successful_creation | 2 |
| a | C | correct_external_fault_detection | 2 |
| a | C | correct_rejection | 2 |
| a | C | correct_timeout_detection | 2 |
| a | C | successful_creation | 2 |
| b | A | correct_external_fault_detection | 2 |
| b | A | correct_rejection | 2 |
| b | A | correct_timeout_detection | 2 |
| b | A | successful_creation | 2 |
| b | B | correct_external_fault_detection | 2 |
| b | B | correct_rejection | 2 |
| b | B | correct_timeout_detection | 2 |
| b | B | successful_creation | 2 |
| b | C | correct_external_fault_detection | 2 |
| b | C | correct_rejection | 2 |
| b | C | correct_timeout_detection | 2 |
| b | C | successful_creation | 2 |

## execution_times

| provider | condition | classification | scope | n | min_seconds | median_seconds | mean_seconds | p95_seconds | max_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | A | correct_external_fault_detection | worker | 2 | 0.06434198199997354 | 0.06439080749998993 | 0.06439080749998993 | 0.06443963300000632 | 0.06443963300000632 |
| a | A | correct_rejection | worker | 2 | 0.06420903800005817 | 0.06425242550005805 | 0.06425242550005805 | 0.06429581300005793 | 0.06429581300005793 |
| a | A | correct_timeout_detection | worker | 2 | 1.001555547999942 | 1.0015856684999562 | 1.0015856684999562 | 1.0016157889999704 | 1.0016157889999704 |
| a | A | successful_creation | worker | 2 | 0.06420659399998385 | 0.08951136650000535 | 0.08951136650000535 | 0.11481613900002685 | 0.11481613900002685 |
| a | A | correct_external_fault_detection | whole_attempt | 2 | 0.5521799179999789 | 0.5529547845000025 | 0.5529547845000025 | 0.553729651000026 | 0.553729651000026 |
| a | A | correct_rejection | whole_attempt | 2 | 0.5010547890000225 | 0.5011364860000072 | 0.5011364860000072 | 0.5012181829999918 | 0.5012181829999918 |
| a | A | correct_timeout_detection | whole_attempt | 2 | 2.053506500000026 | 2.0549409684999773 | 2.0549409684999773 | 2.0563754369999288 | 2.0563754369999288 |
| a | A | successful_creation | whole_attempt | 2 | 0.5540422620000527 | 0.5576151215000209 | 0.5576151215000209 | 0.5611879809999891 | 0.5611879809999891 |
| a | B | correct_external_fault_detection | worker | 2 | 0.06422304900002018 | 0.08942766899997423 | 0.08942766899997423 | 0.11463228899992828 | 0.11463228899992828 |
| a | B | correct_rejection | worker | 2 | 0.06418304800001806 | 0.06418479400002752 | 0.06418479400002752 | 0.06418654000003698 | 0.06418654000003698 |
| a | B | correct_timeout_detection | worker | 2 | 1.0015723589999652 | 1.0015738669999905 | 1.0015738669999905 | 1.0015753750000158 | 1.0015753750000158 |
| a | B | successful_creation | worker | 2 | 0.06428955799992764 | 0.06435523699991563 | 0.06435523699991563 | 0.06442091599990363 | 0.06442091599990363 |
| a | B | correct_external_fault_detection | whole_attempt | 2 | 0.5538434530000131 | 0.5555607684999586 | 0.5555607684999586 | 0.5572780839999041 | 0.5572780839999041 |
| a | B | correct_rejection | whole_attempt | 2 | 0.501093032999961 | 0.5011470029999714 | 0.5011470029999714 | 0.5012009729999818 | 0.5012009729999818 |
| a | B | correct_timeout_detection | whole_attempt | 2 | 2.053090205999979 | 2.0535297604999982 | 2.0535297604999982 | 2.0539693150000176 | 2.0539693150000176 |
| a | B | successful_creation | whole_attempt | 2 | 0.550329515000044 | 0.55132618250002 | 0.55132618250002 | 0.5523228499999959 | 0.5523228499999959 |
| a | C | correct_external_fault_detection | worker | 2 | 0.11447186899999906 | 0.1144831135000004 | 0.1144831135000004 | 0.11449435800000174 | 0.11449435800000174 |
| a | C | correct_rejection | worker | 2 | 0.11429185800000141 | 0.1142965145000403 | 0.1142965145000403 | 0.1143011710000792 | 0.1143011710000792 |
| a | C | correct_timeout_detection | worker | 2 | 1.001503705999994 | 1.0015561185000479 | 1.0015561185000479 | 1.0016085310001017 | 1.0016085310001017 |
| a | C | successful_creation | worker | 2 | 0.11445417699997051 | 0.1154843049999954 | 0.1154843049999954 | 0.11651443300002029 | 0.11651443300002029 |
| a | C | correct_external_fault_detection | whole_attempt | 2 | 0.5902803899999753 | 0.5904847544999825 | 0.5904847544999825 | 0.5906891189999897 | 0.5906891189999897 |
| a | C | correct_rejection | whole_attempt | 2 | 0.5010490739999796 | 0.5011017760000414 | 0.5011017760000414 | 0.5011544780001032 | 0.5011544780001032 |
| a | C | correct_timeout_detection | whole_attempt | 2 | 2.087041353000018 | 2.087332270499985 | 2.087332270499985 | 2.0876231879999523 | 2.0876231879999523 |
| a | C | successful_creation | whole_attempt | 2 | 0.5831789329999992 | 0.5867250829999762 | 0.5867250829999762 | 0.5902712329999531 | 0.5902712329999531 |
| b | A | correct_external_fault_detection | worker | 2 | 0.0642766409999922 | 0.06437198050002735 | 0.06437198050002735 | 0.0644673200000625 | 0.0644673200000625 |
| b | A | correct_rejection | worker | 2 | 0.06433508199995686 | 0.06439640099995358 | 0.06439640099995358 | 0.06445771999995031 | 0.06445771999995031 |
| b | A | correct_timeout_detection | worker | 2 | 1.0015749170000845 | 1.0015751685000396 | 1.0015751685000396 | 1.0015754199999947 | 1.0015754199999947 |
| b | A | successful_creation | worker | 2 | 0.06418267399999422 | 0.06434954850004715 | 0.06434954850004715 | 0.06451642300010008 | 0.06451642300010008 |
| b | A | correct_external_fault_detection | whole_attempt | 2 | 0.5510320199999796 | 0.5516484314999843 | 0.5516484314999843 | 0.552264842999989 | 0.552264842999989 |
| b | A | correct_rejection | whole_attempt | 2 | 0.501129350000042 | 0.5011602515000391 | 0.5011602515000391 | 0.5011911530000361 | 0.5011911530000361 |
| b | A | correct_timeout_detection | whole_attempt | 2 | 2.054062163000026 | 2.06694029800002 | 2.06694029800002 | 2.079818433000014 | 2.079818433000014 |
| b | A | successful_creation | whole_attempt | 2 | 0.5519692400000622 | 0.5537369370000533 | 0.5537369370000533 | 0.5555046340000445 | 0.5555046340000445 |
| b | B | correct_external_fault_detection | worker | 2 | 0.06439302000001135 | 0.06445338899999342 | 0.06445338899999342 | 0.0645137579999755 | 0.0645137579999755 |
| b | B | correct_rejection | worker | 2 | 0.06418680100000529 | 0.06421711749999304 | 0.06421711749999304 | 0.06424743399998079 | 0.06424743399998079 |
| b | B | correct_timeout_detection | worker | 2 | 1.0014941210000643 | 1.0015888045000452 | 1.0015888045000452 | 1.001683488000026 | 1.001683488000026 |
| b | B | successful_creation | worker | 2 | 0.06437074799998754 | 0.08951744799998096 | 0.08951744799998096 | 0.11466414799997438 | 0.11466414799997438 |
| b | B | correct_external_fault_detection | whole_attempt | 2 | 0.5513552800000525 | 0.5515567115000408 | 0.5515567115000408 | 0.5517581430000291 | 0.5517581430000291 |
| b | B | correct_rejection | whole_attempt | 2 | 0.5008917549999978 | 0.5009298280000394 | 0.5009298280000394 | 0.5009679010000809 | 0.5009679010000809 |
| b | B | correct_timeout_detection | whole_attempt | 2 | 2.0533399419999796 | 2.0540258445000177 | 2.0540258445000177 | 2.0547117470000558 | 2.0547117470000558 |
| b | B | successful_creation | whole_attempt | 2 | 0.5514099530000749 | 0.5578821295000012 | 0.5578821295000012 | 0.5643543059999274 | 0.5643543059999274 |
| b | C | correct_external_fault_detection | worker | 2 | 0.11433265000005122 | 0.1144695520000596 | 0.1144695520000596 | 0.11460645400006797 | 0.11460645400006797 |
| b | C | correct_rejection | worker | 2 | 0.11416162699993038 | 0.1143471109999723 | 0.1143471109999723 | 0.11453259500001423 | 0.11453259500001423 |
| b | C | correct_timeout_detection | worker | 2 | 1.0015721269999176 | 1.0015738704999535 | 1.0015738704999535 | 1.0015756139999894 | 1.0015756139999894 |
| b | C | successful_creation | worker | 2 | 0.11442535700007284 | 0.11463295350000635 | 0.11463295350000635 | 0.11484054999993987 | 0.11484054999993987 |
| b | C | correct_external_fault_detection | whole_attempt | 2 | 0.5821876649999922 | 0.5838122834999808 | 0.5838122834999808 | 0.5854369019999695 | 0.5854369019999695 |
| b | C | correct_rejection | whole_attempt | 2 | 0.5010748969999668 | 0.5011179649999349 | 0.5011179649999349 | 0.501161032999903 | 0.501161032999903 |
| b | C | correct_timeout_detection | whole_attempt | 2 | 2.086876081000014 | 2.0869231975000275 | 2.0869231975000275 | 2.086970314000041 | 2.086970314000041 |
| b | C | successful_creation | whole_attempt | 2 | 0.5835003419999794 | 0.5854629675000069 | 0.5854629675000069 | 0.5874255930000345 | 0.5874255930000345 |

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
