#include "identity/identity_registry.hpp"
#include <cassert>

using ds2online::identity::ExternalIdentity;
using ds2online::identity::IdentityRegistry;

int main() {
    IdentityRegistry registry;
    const ExternalIdentity steam_user{"steam", {0x10, 0x20}};
    const ExternalIdentity other_provider{"unverified", {0x10, 0x20}};
    const ExternalIdentity second_user{"steam", {0x10, 0x21}};
    const ExternalIdentity invalid{"", {0x01}};

    assert(!registry.Find(steam_user).has_value());
    const auto first_id = registry.ResolveOrCreate(steam_user);
    assert(first_id.has_value() && *first_id == 1);

    const auto same_id = registry.ResolveOrCreate(steam_user);
    assert(same_id.has_value() && *same_id == *first_id);

    const auto provider_scoped_id = registry.ResolveOrCreate(other_provider);
    assert(provider_scoped_id.has_value() && *provider_scoped_id != *first_id);

    const auto second_id = registry.ResolveOrCreate(second_user);
    assert(second_id.has_value());
    assert(*second_id != *first_id && *second_id != *provider_scoped_id);
    assert(registry.Find(steam_user) == first_id);

    assert(!registry.ResolveOrCreate(invalid).has_value());
    assert(!registry.Find(invalid).has_value());
    return 0;
}
