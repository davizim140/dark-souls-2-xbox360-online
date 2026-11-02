from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ProjectStructureTests(unittest.TestCase):
    def test_required_docs_exist(self):
        for relative in (
            "README.md",
            "docs/architecture.md",
            "docs/research-plan.md",
            "docs/protocol/xbox360-connection-failure-analysis.md",
            "docs/compatibility/ds2-breakin-visitor-manager-audit.md",
            "docs/compatibility/ds2-player-data-state-audit.md",
            "docs/compatibility/ds2-character-persistence-audit.md",
            "docs/compatibility/ds2-upstream-steam-dependency-audit.md",
            "docs/compatibility/ds2-steam-identity-dependency-audit.md",
            "docs/protocol/ds2-allstatus-protobuf-field-audit.md",
            "docs/protocol/ds2-player-status-upload-config-audit.md",
            "docs/compatibility/ds2-matchmaking-manager-audit.md",
            "docs/compatibility/ds2-ghosts-messages-bloodstains-audit.md",
            ".github/workflows/ci.yml",
            "backend/include/identity/external_identity.hpp",
            "backend/tests/external_identity_test.cpp",
            "backend/include/identity/identity_registry.hpp",
            "backend/tests/identity_registry_test.cpp",
            "docs/architecture/identity-registry.md",
            "docs/architecture/session-registry.md",
            "backend/include/matchmaking/session_registry.hpp",
            "backend/include/matchmaking/matchmaking_coordinator.hpp",
            "backend/tests/matchmaking_coordinator_test.cpp",
            "docs/architecture/matchmaking-coordinator.md",
            "backend/include/presence/presence_registry.hpp",
            "backend/tests/presence_registry_test.cpp",
            "docs/architecture/presence-registry.md",
            "backend/tests/session_registry_test.cpp",
            "docs/compatibility/ds2-identity-migration-audit.md",
            "docs/compatibility/ds2-copy-migration-contract.md",
            "docs/compatibility/dsos-ds2-pc-client-redirection-audit.md",
            "docs/compatibility/dsos-xboxone-stubs-not-xbox360-audit.md",
            "docs/protocol/dsos-login-auth-game-server-chain-audit.md",
            "docs/protocol/ds2-reliable-udp-message-opcode-audit.md",
            "docs/compatibility/ds2-message-handler-coverage-audit.md",
            "docs/compatibility/ds2-handler-gaps-and-uncertainties-audit.md",
            "docs/compatibility/ds2-push-emission-coverage-audit.md",
            "docs/compatibility/ds2-xbox360-scholar-recomp-reference-audit.md",
            "docs/compatibility/ds2-xam-session-live-party-voice-shim-audit.md",
            "docs/compatibility/ds2-request-send-message-to-players-security-audit.md",
            "backend/include/identity/sqlite_identity_store.hpp",
            "backend/src/identity/sqlite_identity_store.cpp",
            "backend/tests/sqlite_identity_store_test.cpp",
            "tools/inspect_dsos_identity_db.py",
            "tools/migrate_dsos_identity_copy.py",
            "tests/test_dsos_db_inspector.py",
            "tests/test_dsos_identity_migration.py",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)


    def test_session_registry_scope_and_contract(self):
        header = (ROOT / "backend/include/matchmaking/session_registry.hpp").read_text(encoding="utf-8")
        docs = (ROOT / "docs/architecture/session-registry.md").read_text(encoding="utf-8")
        self.assertIn("SessionRegistry", header)
        self.assertIn("SessionFull", header)
        self.assertIn("SessionNotFound", header)
        self.assertIn("not yet a network server", docs)
        self.assertIn("Xbox Live/XONLINE integration", docs)

    def test_matchmaking_coordinator_requires_fresh_presence(self):
        header = (ROOT / "backend/include/matchmaking/matchmaking_coordinator.hpp").read_text(encoding="utf-8")
        docs = (ROOT / "docs/architecture/matchmaking-coordinator.md").read_text(encoding="utf-8")
        self.assertIn("MatchmakingCoordinator", header)
        self.assertIn("PlayerOffline", header)
        self.assertIn("FindActive", header)
        self.assertIn("not DS2 matchmaking", docs)
        self.assertIn("Xbox Live/XONLINE", docs)

    def test_presence_registry_contract_is_explicit(self):
        header = (ROOT / "backend/include/presence/presence_registry.hpp").read_text(encoding="utf-8")
        docs = (ROOT / "docs/architecture/presence-registry.md").read_text(encoding="utf-8")
        self.assertIn("PresenceRegistry", header)
        self.assertIn("MarkOnline", header)
        self.assertIn("Expire", header)
        self.assertIn("not a network service", docs)
        self.assertIn("Xbox Live/XONLINE", docs)

    def test_status_is_honest(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("fase de levantamento técnico", readme)
        self.assertIn("Não implementado", readme)
        self.assertNotIn("XEX funcional já compilado", readme)

    def test_plan_requires_evidence(self):
        plan = (ROOT / "docs/research-plan.md").read_text(encoding="utf-8")
        self.assertIn("Title ID", plan)
        self.assertIn("evidências", plan.lower())

    def test_dsos_pc_redirect_is_not_misrepresented_as_xbox_support(self):
        report = (ROOT / "docs/compatibility/dsos-ds2-pc-client-redirection-audit.md").read_text(encoding="utf-8").lower()
        self.assertIn("50031", report)
        self.assertIn("winsock", report)
        self.assertIn("injector.dll", report)
        self.assertIn("steam", report)
        self.assertIn("protocolo xbox permanece não identificado", report)

    def test_dsos_xboxone_stubs_are_not_claimed_as_xbox360_support(self):
        report = (ROOT / "docs/compatibility/dsos-xboxone-stubs-not-xbox360-audit.md").read_text(encoding="utf-8").lower()
        self.assertIn("requestqueryloginserverinfoforxboxone", report)
        self.assertIn("getservicestatusforxboxone", report)
        self.assertIn("loginclient.cpp", report)
        self.assertIn("steamticket", report)
        self.assertIn("não é evidência de xbox 360", report)
        self.assertIn("não cria xex", report)

    def test_dsos_server_chain_audit_marks_pc_assumptions(self):
        report = (ROOT / "docs/protocol/dsos-login-auth-game-server-chain-audit.md").read_text(encoding="utf-8").lower()
        self.assertIn("requestqueryloginserverinfo", report)
        self.assertIn("steamticket", report)
        self.assertIn("beginauthsession", report)
        self.assertIn("uint64_t authtoken", report)
        self.assertIn("netconnectionudp", report)
        self.assertIn("não prova que o xbox 360", report)
        self.assertIn("nenhum xex criado ou executado", report)


    def test_ds2_reliable_udp_opcode_audit_covers_active_map(self):
        report = (ROOT / "docs/protocol/ds2-reliable-udp-message-opcode-audit.md").read_text(encoding="utf-8")
        self.assertIn("82 registros ativos", report)
        self.assertEqual(report.count("| `0X"), 82)
        self.assertIn("`0X0394`", report)
        self.assertIn("`0X03D3`", report)
        self.assertIn("`msg_type = 0x0320`", report)
        self.assertIn("não comprova que o Xbox 360", report)
        self.assertIn("Nenhum XEX foi criado ou executado", report)


    def test_ds2_message_handler_coverage_audit_is_explicit(self):
        report = (ROOT / "docs/compatibility/ds2-message-handler-coverage-audit.md").read_text(encoding="utf-8")
        self.assertIn("82", report)
        self.assertIn("19", report)
        self.assertIn("63", report)
        self.assertIn("62", report)
        self.assertIn("`RequestNotifyRingBell`", report)
        self.assertIn("`0x03EE`", report)
        self.assertIn("não identificados", report)
        self.assertIn("Nenhum XEX foi criado ou executado", report)


    def test_ds2_handler_gaps_audit_distinguishes_unknowns_from_stubs(self):
        report = (ROOT / "docs/compatibility/ds2-handler-gaps-and-uncertainties-audit.md").read_text(encoding="utf-8")
        for evidence in (
            "`max_type_1`",
            "`RequestUpdateQuickMatch`",
            "`Handle_RequestRejectSign`",
            "`Handle_RequestRejectMirrorKnightSign`",
            "resposta protobuf vazia",
            "Não provam",
            "Nenhum XEX foi criado ou executado",
        ):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, report)


    def test_ds2_push_emission_audit_marks_unemitted_types_as_unconfirmed(self):
        report = (ROOT / "docs/compatibility/ds2-push-emission-coverage-audit.md").read_text(encoding="utf-8")
        self.assertIn("19 tipos de push", report)
        self.assertIn("17", report)
        self.assertIn("`PushRequestAllowQuickMatch`", report)
        self.assertIn("`PushRequestRemoveQuickMatch`", report)
        self.assertIn("Sem emissão direta encontrada", report)
        self.assertIn("Handle_RequestSendMessageToPlayers", report)
        self.assertIn("SendRawProtobuf", report)
        self.assertIn("retransmissão de push enviado pelo cliente", report)
        self.assertIn("17 pushes com emissão direta encontrada; 2 sem emissão direta encontrada", report)
        self.assertIn("não confirma que o Xbox 360", report)
        self.assertIn("Nenhum XEX foi criado ou executado", report)


    def test_ds2_client_message_relay_security_audit_records_validation_limits(self):
        report = (ROOT / "docs/compatibility/ds2-request-send-message-to-players-security-audit.md").read_text(encoding="utf-8")
        for evidence in (
            "`SEND_MESSAGE_TO_PLAYERS_SANITY_CHECKS`",
            "`NRSSR_SANITY_CHECKS`",
            "6 entradas",
            "`ValidateEntryList`",
            "retorna imediatamente `Valid`",
            "`PushRequestAllowQuickMatch`",
            "`SendRawProtobuf`",
            "não foi encontrada uma verificação explícita",
            "protocolo Xbox 360 permanece não identificado",
            "Nenhum XEX foi criado ou executado",
        ):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, report)


    def test_ds2_disconnect_cleanup_coverage_audit_is_precise(self):
        report = (ROOT / "docs/compatibility/ds2-disconnect-cleanup-coverage-audit.md").read_text(encoding="utf-8")
        for evidence in (
            "`GameService::Poll()`",
            "`OnLostPlayer`",
            "`DS2_BreakInManager::OnLostPlayer`",
            "`ActiveSummonSigns`",
            "`ActiveMirrorKnightSummonSigns`",
            "`HostPlayerId`",
            "não declara override",
            "não prova, por si só, vazamento",
            "protocolo Xbox 360 continua não identificado",
            "Nenhum XEX foi criado ou executado",
        ):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, report)



    def test_xam_session_live_party_voice_shim_audit_is_scoped(self):
        report = (ROOT / "docs/compatibility/ds2-xam-session-live-party-voice-shim-audit.md").read_text(encoding="utf-8")
        for evidence in (
            "`XamSessionCreateHandle`",
            "`XamSessionRefObjByHandle`",
            "`XamPartyJoin`",
            "`X_ERROR_FUNCTION_FAILED`",
            "`XONLINE_NAT_OPEN`",
            "`ERROR_CONNECTION_INVALID`",
            "`XamVoiceCreate`",
            "não prova que o jogo importe",
            "Nenhum XEX foi criado ou executado",
        ):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, report)

    def test_scholar_xbox360_recompiler_reference_is_scoped_and_honest(self):
        report = (ROOT / "docs/compatibility/ds2-xbox360-scholar-recomp-reference-audit.md").read_text(encoding="utf-8")
        for evidence in (
            "`465307E4`",
            "`0.0.0.22`",
            "`XNET`",
            "`XONLINE`",
            "`NetDll_XNetGetTitleXnAddr`",
            "`NetDll_XNetDnsLookup`",
            "stubs/shims do ambiente ReXGlue",
            "não demonstra compatibilidade",
            "Nenhum XEX foi criado ou executado",
        ):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, report)

    def test_xbox_connection_failure_does_not_claim_unknown_protocol_details(self):
        report = (ROOT / "docs/protocol/xbox360-connection-failure-analysis.md").read_text(encoding="utf-8").lower()
        self.assertIn("protocolo xbox 360 não identificado", report)
        self.assertIn("não identifica qual etapa falhou", report)
        self.assertIn("hostname", report)
        self.assertIn("desconhecida", report)
        self.assertIn("não implementar ainda", report)

    def test_upstream_audits_preserve_xbox_compatibility_boundary(self):
        paths = (
            "docs/compatibility/ds2-breakin-visitor-manager-audit.md",
            "docs/compatibility/ds2-player-data-state-audit.md",
            "docs/compatibility/ds2-character-persistence-audit.md",
            "docs/compatibility/ds2-upstream-steam-dependency-audit.md",
            "docs/protocol/ds2-allstatus-protobuf-field-audit.md",
            "docs/compatibility/ds2-matchmaking-manager-audit.md",
            "docs/compatibility/ds2-ghosts-messages-bloodstains-audit.md",
        )
        for relative in paths:
            with self.subTest(path=relative):
                content = (ROOT / relative).read_text(encoding="utf-8").lower()
                self.assertIn("xbox", content)
                self.assertTrue("não" in content or "not" in content)

if __name__ == "__main__":
    unittest.main(verbosity=2)
