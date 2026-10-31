#include "identity/external_identity.hpp"

#include <cassert>
#include <cstdint>
#include <vector>

using ds2online::identity::ExternalIdentity;

int main() {
    const ExternalIdentity steam_a{"steam", {0x01, 0x02, 0x03}};
    const ExternalIdentity steam_b{"steam", {0x01, 0x02, 0x03}};
    const ExternalIdentity other_namespace{"unverified", {0x01, 0x02, 0x03}};

    assert(steam_a.IsValid());
    assert(steam_a == steam_b);
    assert(steam_a != other_namespace);

    assert(!ExternalIdentity{"", {0x01}}.IsValid());
    assert(!ExternalIdentity{"steam", {}}.IsValid());
    assert(!ExternalIdentity{"Steam", {0x01}}.IsValid());
    assert(!ExternalIdentity{"steam", std::vector<std::uint8_t>(129, 0x01)}.IsValid());

    return 0;
}
