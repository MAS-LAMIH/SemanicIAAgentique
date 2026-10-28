# Visible-provider runtime results

Diagnostic verdict: FAIL. Independent providers: 2; measured integrations: 0.

## correctness

| provider | condition | attempts | diagnostic_passed | successful_creations | native_state_correct | unexpected_mutations |
| --- | --- | --- | --- | --- | --- | --- |
| a | A | 4 | 4 | 1 | 2 | 1 |
| a | B | 4 | 4 | 1 | 2 | 1 |
| a | C | 4 | 4 | 1 | 2 | 1 |
| b | A | 4 | 4 | 1 | 2 | 1 |
| b | B | 4 | 4 | 1 | 2 | 1 |
| b | C | 4 | 4 | 1 | 2 | 1 |

## error_handling

| provider | condition | classification | count |
| --- | --- | --- | --- |
| a | A | correct_external_fault_detection | 1 |
| a | A | correct_rejection | 1 |
| a | A | correct_timeout_detection | 1 |
| a | A | successful_creation | 1 |
| a | B | correct_external_fault_detection | 1 |
| a | B | correct_rejection | 1 |
| a | B | correct_timeout_detection | 1 |
| a | B | successful_creation | 1 |
| a | C | correct_external_fault_detection | 1 |
| a | C | correct_rejection | 1 |
| a | C | correct_timeout_detection | 1 |
| a | C | successful_creation | 1 |
| b | A | correct_external_fault_detection | 1 |
| b | A | correct_rejection | 1 |
| b | A | correct_timeout_detection | 1 |
| b | A | successful_creation | 1 |
| b | B | correct_external_fault_detection | 1 |
| b | B | correct_rejection | 1 |
| b | B | correct_timeout_detection | 1 |
| b | B | successful_creation | 1 |
| b | C | correct_external_fault_detection | 1 |
| b | C | correct_rejection | 1 |
| b | C | correct_timeout_detection | 1 |
| b | C | successful_creation | 1 |

## execution_times

| provider | condition | classification | scope | n | min_seconds | median_seconds | mean_seconds | p95_seconds | max_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | A | correct_external_fault_detection | worker | 1 | 0.06420140899990656 | 0.06420140899990656 | 0.06420140899990656 | 0.06420140899990656 | 0.06420140899990656 |
| a | A | correct_rejection | worker | 1 | 0.06441192099998716 | 0.06441192099998716 | 0.06441192099998716 | 0.06441192099998716 | 0.06441192099998716 |
| a | A | correct_timeout_detection | worker | 1 | 1.0015915289999384 | 1.0015915289999384 | 1.0015915289999384 | 1.0015915289999384 | 1.0015915289999384 |
| a | A | successful_creation | worker | 1 | 0.06436066899993875 | 0.06436066899993875 | 0.06436066899993875 | 0.06436066899993875 | 0.06436066899993875 |
| a | A | correct_external_fault_detection | whole_attempt | 1 | 0.5499002649999056 | 0.5499002649999056 | 0.5499002649999056 | 0.5499002649999056 | 0.5499002649999056 |
| a | A | correct_rejection | whole_attempt | 1 | 0.5010922440000058 | 0.5010922440000058 | 0.5010922440000058 | 0.5010922440000058 | 0.5010922440000058 |
| a | A | correct_timeout_detection | whole_attempt | 1 | 2.053142491000017 | 2.053142491000017 | 2.053142491000017 | 2.053142491000017 | 2.053142491000017 |
| a | A | successful_creation | whole_attempt | 1 | 0.5551783290000003 | 0.5551783290000003 | 0.5551783290000003 | 0.5551783290000003 | 0.5551783290000003 |
| a | B | correct_external_fault_detection | worker | 1 | 0.06425740499992116 | 0.06425740499992116 | 0.06425740499992116 | 0.06425740499992116 | 0.06425740499992116 |
| a | B | correct_rejection | worker | 1 | 0.06456954299994777 | 0.06456954299994777 | 0.06456954299994777 | 0.06456954299994777 | 0.06456954299994777 |
| a | B | correct_timeout_detection | worker | 1 | 1.001620250999963 | 1.001620250999963 | 1.001620250999963 | 1.001620250999963 | 1.001620250999963 |
| a | B | successful_creation | worker | 1 | 0.06437025499997162 | 0.06437025499997162 | 0.06437025499997162 | 0.06437025499997162 | 0.06437025499997162 |
| a | B | correct_external_fault_detection | whole_attempt | 1 | 0.552217048999978 | 0.552217048999978 | 0.552217048999978 | 0.552217048999978 | 0.552217048999978 |
| a | B | correct_rejection | whole_attempt | 1 | 0.501087028000029 | 0.501087028000029 | 0.501087028000029 | 0.501087028000029 | 0.501087028000029 |
| a | B | correct_timeout_detection | whole_attempt | 1 | 2.052532090999989 | 2.052532090999989 | 2.052532090999989 | 2.052532090999989 | 2.052532090999989 |
| a | B | successful_creation | whole_attempt | 1 | 0.5522423879999678 | 0.5522423879999678 | 0.5522423879999678 | 0.5522423879999678 | 0.5522423879999678 |
| a | C | correct_external_fault_detection | worker | 1 | 0.11443631700001333 | 0.11443631700001333 | 0.11443631700001333 | 0.11443631700001333 | 0.11443631700001333 |
| a | C | correct_rejection | worker | 1 | 0.11439366499996595 | 0.11439366499996595 | 0.11439366499996595 | 0.11439366499996595 | 0.11439366499996595 |
| a | C | correct_timeout_detection | worker | 1 | 1.0015642960000832 | 1.0015642960000832 | 1.0015642960000832 | 1.0015642960000832 | 1.0015642960000832 |
| a | C | successful_creation | worker | 1 | 0.11445436799999698 | 0.11445436799999698 | 0.11445436799999698 | 0.11445436799999698 | 0.11445436799999698 |
| a | C | correct_external_fault_detection | whole_attempt | 1 | 0.5830598159999454 | 0.5830598159999454 | 0.5830598159999454 | 0.5830598159999454 | 0.5830598159999454 |
| a | C | correct_rejection | whole_attempt | 1 | 0.501118768000083 | 0.501118768000083 | 0.501118768000083 | 0.501118768000083 | 0.501118768000083 |
| a | C | correct_timeout_detection | whole_attempt | 1 | 2.084080121999932 | 2.084080121999932 | 2.084080121999932 | 2.084080121999932 | 2.084080121999932 |
| a | C | successful_creation | whole_attempt | 1 | 0.5838129320000007 | 0.5838129320000007 | 0.5838129320000007 | 0.5838129320000007 | 0.5838129320000007 |
| b | A | correct_external_fault_detection | worker | 1 | 0.06432888199992703 | 0.06432888199992703 | 0.06432888199992703 | 0.06432888199992703 | 0.06432888199992703 |
| b | A | correct_rejection | worker | 1 | 0.06448433500008832 | 0.06448433500008832 | 0.06448433500008832 | 0.06448433500008832 | 0.06448433500008832 |
| b | A | correct_timeout_detection | worker | 1 | 1.0015873210001018 | 1.0015873210001018 | 1.0015873210001018 | 1.0015873210001018 | 1.0015873210001018 |
| b | A | successful_creation | worker | 1 | 0.06439904799992746 | 0.06439904799992746 | 0.06439904799992746 | 0.06439904799992746 | 0.06439904799992746 |
| b | A | correct_external_fault_detection | whole_attempt | 1 | 0.5513271329999725 | 0.5513271329999725 | 0.5513271329999725 | 0.5513271329999725 | 0.5513271329999725 |
| b | A | correct_rejection | whole_attempt | 1 | 0.5011705580000125 | 0.5011705580000125 | 0.5011705580000125 | 0.5011705580000125 | 0.5011705580000125 |
| b | A | correct_timeout_detection | whole_attempt | 1 | 2.055043578999971 | 2.055043578999971 | 2.055043578999971 | 2.055043578999971 | 2.055043578999971 |
| b | A | successful_creation | whole_attempt | 1 | 0.5547594770000615 | 0.5547594770000615 | 0.5547594770000615 | 0.5547594770000615 | 0.5547594770000615 |
| b | B | correct_external_fault_detection | worker | 1 | 0.06413430800000697 | 0.06413430800000697 | 0.06413430800000697 | 0.06413430800000697 | 0.06413430800000697 |
| b | B | correct_rejection | worker | 1 | 0.06420645299999705 | 0.06420645299999705 | 0.06420645299999705 | 0.06420645299999705 | 0.06420645299999705 |
| b | B | correct_timeout_detection | worker | 1 | 1.0015779880000082 | 1.0015779880000082 | 1.0015779880000082 | 1.0015779880000082 | 1.0015779880000082 |
| b | B | successful_creation | worker | 1 | 0.06465956200008804 | 0.06465956200008804 | 0.06465956200008804 | 0.06465956200008804 | 0.06465956200008804 |
| b | B | correct_external_fault_detection | whole_attempt | 1 | 0.5515002089999825 | 0.5515002089999825 | 0.5515002089999825 | 0.5515002089999825 | 0.5515002089999825 |
| b | B | correct_rejection | whole_attempt | 1 | 0.5011360670000613 | 0.5011360670000613 | 0.5011360670000613 | 0.5011360670000613 | 0.5011360670000613 |
| b | B | correct_timeout_detection | whole_attempt | 1 | 2.0521079359999703 | 2.0521079359999703 | 2.0521079359999703 | 2.0521079359999703 | 2.0521079359999703 |
| b | B | successful_creation | whole_attempt | 1 | 0.5535738689999334 | 0.5535738689999334 | 0.5535738689999334 | 0.5535738689999334 | 0.5535738689999334 |
| b | C | correct_external_fault_detection | worker | 1 | 0.11456915700000536 | 0.11456915700000536 | 0.11456915700000536 | 0.11456915700000536 | 0.11456915700000536 |
| b | C | correct_rejection | worker | 1 | 0.1144183220000059 | 0.1144183220000059 | 0.1144183220000059 | 0.1144183220000059 | 0.1144183220000059 |
| b | C | correct_timeout_detection | worker | 1 | 1.001570255000047 | 1.001570255000047 | 1.001570255000047 | 1.001570255000047 | 1.001570255000047 |
| b | C | successful_creation | worker | 1 | 0.1143693380000741 | 0.1143693380000741 | 0.1143693380000741 | 0.1143693380000741 | 0.1143693380000741 |
| b | C | correct_external_fault_detection | whole_attempt | 1 | 0.5833934139999428 | 0.5833934139999428 | 0.5833934139999428 | 0.5833934139999428 | 0.5833934139999428 |
| b | C | correct_rejection | whole_attempt | 1 | 0.5010894729999791 | 0.5010894729999791 | 0.5010894729999791 | 0.5010894729999791 | 0.5010894729999791 |
| b | C | correct_timeout_detection | whole_attempt | 1 | 2.08922535399995 | 2.08922535399995 | 2.08922535399995 | 2.08922535399995 | 2.08922535399995 |
| b | C | successful_creation | whole_attempt | 1 | 0.5858270420000053 | 0.5858270420000053 | 0.5858270420000053 | 0.5858270420000053 | 0.5858270420000053 |

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
| 11833 | evaluation_infrastructure | v4_pilot/experiment.py | 180 | 83a8dfb663bc4294b530fda7ed419d424590ffc71fe01450ca8dc18aea3cecf6 |
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
