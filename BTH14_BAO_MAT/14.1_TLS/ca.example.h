#pragma once
// Copy to ca.h and replace the complete PEM with your own lab CA certificate.
static const char ROOT_CA[] = R"PEM(
-----BEGIN CERTIFICATE-----
REPLACE_WITH_CONTENTS_OF_certs_ca_crt
-----END CERTIFICATE-----
)PEM";
