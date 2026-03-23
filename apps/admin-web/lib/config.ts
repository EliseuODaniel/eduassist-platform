export type PortalConfig = {
  apiCoreUrl: string;
  adminWebPublicUrl: string;
  keycloakInternalUrl: string;
  keycloakPublicUrl: string;
  keycloakRealm: string;
  keycloakWebClientId: string;
};

export function getPortalConfig(): PortalConfig {
  return {
    apiCoreUrl: process.env.API_CORE_URL ?? 'http://api-core:8000',
    adminWebPublicUrl: process.env.ADMIN_WEB_PUBLIC_URL ?? 'http://localhost:3000',
    keycloakInternalUrl:
      process.env.KEYCLOAK_INTERNAL_URL ??
      process.env.KEYCLOAK_HOST ??
      'http://keycloak:8080',
    keycloakPublicUrl: process.env.KEYCLOAK_PUBLIC_URL ?? 'http://localhost:8080',
    keycloakRealm: process.env.KEYCLOAK_REALM ?? 'eduassist',
    keycloakWebClientId: process.env.KEYCLOAK_WEB_CLIENT_ID ?? 'eduassist-web',
  };
}
