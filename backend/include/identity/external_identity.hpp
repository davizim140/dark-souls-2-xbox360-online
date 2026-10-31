#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace ds2online::identity {

// A namespace-qualified external identifier. The bytes are opaque: this type
// does not authenticate the holder or assert that a platform uses this format.
struct ExternalIdentity {
    std::string provider;
    std::vector<std::uint8_t> value;

    bool IsValid() const noexcept {
        if (provider.empty() || provider.size() > 32 || value.empty() || value.size() > 128) {
            return false;
        }
        for (unsigned char c : provider) {
            const bool lower = c >= 'a' && c <= 'z';
            const bool digit = c >= '0' && c <= '9';
            if (!lower && !digit && c != '-' && c != '_') {
                return false;
            }
        }
        return true;
    }

    bool operator==(const ExternalIdentity& other) const noexcept {
        return provider == other.provider && value == other.value;
    }

    bool operator!=(const ExternalIdentity& other) const noexcept {
        return !(*this == other);
    }
};

} // namespace ds2online::identity
