#include "identity/external_identity.hpp"

#include <cassert>
#include <cstdint>
#include <vector>

using ds2online::identity::ExternalIdentity;

int main() {
    const ExternalIdentity steam_a{"steam", {0x01, 0x02, 0x03}};
    const ExternalIdentity steam_b{"steam", {0x01, 0x02, 0x03}};
    const ExternalIdentity other_namespace{"unverified", {0x01, 0x02, 0x03}};
    const ExternalIdentity empty_provider{"", {0x01}};
    const ExternalIdentity empty_value{"steam", {}};
    const ExternalIdentity uppercase_provider{"Steam", {0x01}};
    const ExternalIdentity oversized_value{"steam", std::vector<std::uint8_t>(129, 0x01)};

    assert(steam_a.IsValid());
    assert(steam_a == steam_b);
    assert(steam_a != other_namespace);
    assert(!empty_provider.IsValid());
    assert(!empty_value.IsValid());
    assert(!uppercase_provider.IsValid());
    assert(!oversized_value.IsValid());

    return 0;
}
