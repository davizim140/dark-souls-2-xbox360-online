# Auditoria protobuf: AllStatus e dados do personagem (DS2)

- Upstream: `TLeonardUK/ds3os`
- Commit auditado: `56406879a31505a71bea8c6290da370067f43659`
- Schema: [DS2_Frpg2PlayerData.proto](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Protobuf/DarkSouls2/DS2_Frpg2PlayerData.proto)
- Consumo server-side: [DS2_PlayerDataManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/PlayerData/DS2_PlayerDataManager.cpp)

## 1. Estrutura raiz

O protobuf proto2 `AllStatus` possui 10 mensagens opcionais:

| Campo | Número | Tipo |
|---|---:|---|
| player_location | 1 | PlayerLocation |
| player_status | 2 | PlayerStatus |
| item_using_info | 3 | ItemUsingInfo |
| stats_info | 4 | StatsInfo |
| attributes | 5 | LevelStatus |
| physical_status | 6 | PhysicalStatus |
| weapon_status | 7 | WeaponStatus |
| armor_status | 8 | ArmorStatus |
| server_side_status | 9 | ServerSideStatus |
| equipment_info | 10 | EquipmentInfo |

Os números são tags protobuf do schema upstream, não offsets de memória nem posições em um pacote bruto.

## 2. Campos com significado identificado no schema/código

### Localização — PlayerLocation
- `online_area_id` (1): área online atual.
- `cell_id` (2): identificador de célula; o comentário contém valores de exemplo, sem explicar a codificação.
- `online_activity_area_id` (3): área de atividade online; o manager usa zero como condição de não elegibilidade online.
- `position` (4): vetor x/y/z.
- `unknown_5` (5): permanece sem significado confirmado.

### Personagem — PlayerStatus
- `name` (1), `archetype` (2), `covenant` (3).
- `sitting_at_bonfire` (7): usado pelo manager na regra de invadibilidade.
- `phantom_leave_at` (8): contém um campo desconhecido e uma data/hora.
- `disable_cross_region_play` (9).
- `character_id` (10).
- `human_effigy_burnt` (11): usado pelo manager na regra de invadibilidade.
- `played_areas` (12): lista de áreas jogadas.
- `soul_level` (15), `play_time_seconds` (18), `soul_memory` (19).
- Campos 4–6, 13–14, 16–17, 20–21: desconhecidos no schema; comentários fornecem poucos valores observados para alguns, insuficientes para nomear sua função.

### Itens ativos — ItemUsingInfo
- `named_ring_god` (1).
- `using_dried_fingers` (2).
- `guardians_seal` (4), `bell_keepers_seal` (5), `crest_of_the_rat` (6).
- Campos 3, 7 e 8: desconhecidos.

### Atributos — LevelStatus
- Vigor (1), endurance (2), vitality (3), attunement (4), strength (5; grafado `strenght` no schema), dexterity (6), intelligence (7), faith (8) e adaptability (9).

### Estatísticas — StatsInfo
- `sinner_points` (3).
- `bonfire_levels` (4): pares bonfire ID / nível.
- `unlocked_bonfires` (19).
- `datetime` (17).
- `phantom_type_count_6/7/8/9`: contagens estruturadas, mas a semântica de cada grupo não está explicada.
- Demais campos (1, 2, 5, 10–16, 18, 20–21) permanecem desconhecidos.

### Estado físico — PhysicalStatus
- `health` (1), `stamina` (2), `equip_load` (3), `attack_strength` (6), `attack_dexterity` (7), `physical_defence` (14), `petrify_resist` (21), `curse_resist` (22), `agility` (23), `poise` (24).
- Campos 4–5, 8–13 e 15–20 permanecem desconhecidos. Comentários relacionam alguns valores a atributos, mas não estabelecem seus nomes/fórmulas.

### Equipamento e combate
- `WeaponStatus`: seis slots identificados apenas como left/right AR 1–3; significado detalhado de AR não está estabelecido no arquivo.
- `ArmorStatus`: strike, slash e thrust defense; poise.
- `EquipmentInfo`: contagens de slots de armas, armaduras, anéis, munições, belt e magias.

### ServerSideStatus
- Apenas `unknown_1` está declarado; não atribuir significado.

## 3. Como o servidor usa esses dados

A auditoria do manager mostra que o servidor:
- Faz parse de `AllStatus` a partir dos bytes do campo `status` recebido em `RequestUpdatePlayerStatus`.
- Mescla o status recebido ao estado em memória do jogador.
- Extrai nome, áreas, Soul Memory e Soul Level.
- Usa bonfire, Human Effigy e área de atividade para calcular invadibilidade.
- Usa pacto e campos de itens ativos para classificar o visitor pool.
- Lê sinner points para regras de Blue Eye Orb.
- Lê bonfires desbloqueadas para detectar novas descobertas.

Nem todo campo do schema é consumido pelo manager. Existir no protobuf não prova que o servidor dependa dele.

## 4. Regras de interpretação

- `optional` significa que a presença do campo é independente; não se deve presumir que todo cliente envie todos os campos em todo update.
- `repeated` representa uma coleção, não um valor escalar.
- Números entre parênteses são tags protobuf, não offsets.
- Os nomes `unknown_N` são rótulos de pesquisa, não nomes funcionais.
- Comentários com valores de exemplo não são uma especificação de enumeração ou codificação.

## 5. Limite de compatibilidade Xbox

Este é o schema que o servidor DSOS usa para seu caminho DS2. Não comprova que o executável retail Xbox 360 envie o mesmo `AllStatus`, os mesmos números de campo ou o mesmo envelope protobuf. A falha de conexão observada no console não permite identificar se esse payload chegou a ser enviado.

Não foi criado parser para dados Xbox, patch, cliente, servidor funcional ou XEX nesta etapa.

## 6. Próxima investigação

Inspecionar o mecanismo de `PlayerStatusUploadConfig`: máscara de campos, intervalos e merge do status no DS2 upstream. Registrar quais configurações são defaults do DSOS e quais dependem de conhecimento empírico do cliente PC. Não transportar esses valores para Xbox sem evidência.
