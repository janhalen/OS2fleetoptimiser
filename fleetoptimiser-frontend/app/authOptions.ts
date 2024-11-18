import { AuthOptions } from 'next-auth';
import KeycloakProvider from 'next-auth/providers/keycloak';
import jwt_decode from 'jwt-decode';

export const authOptions: AuthOptions = {
  session: {
    strategy: 'jwt',
  },
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_ID!,
      clientSecret: process.env.KEYCLOAK_SECRET!,
      issuer: process.env.KEYCLOAK_ISSUER!,
    }),
  ],
  callbacks: {
    jwt({ token, user, account }) {
    // If initial sign-in, extract roleValue from account.id_token
    if (account && account.id_token) {
      const decoded = jwt_decode(account.id_token);
      // @ts-ignore
      token.roleValue = decoded.privileges_b64;
    }

    // Proceed only if roleValue is available
    // @ts-ignore
    if (token.roleValue) {
      // @ts-ignore
      const decodedRoles = Buffer.from(token.roleValue, 'base64').toString('utf8');

      // Check for write privilege
      if (process.env.ROLE_CHECK) {
        // @ts-ignore
        token.role_valid = decodedRoles.includes(process.env.ROLE_CHECK);
        // @ts-ignore
        token.write_privilege = token.role_valid;
      }
      // @ts-ignore
      if (process.env.ROLE_CHECK_READ && !token.role_valid) {
        // Check for read privilege if write privilege is not granted
        // @ts-ignore
        token.role_valid = decodedRoles.includes(process.env.ROLE_CHECK_READ);
        // @ts-ignore
        token.write_privilege = false;
      }

      if (!process.env.ROLE_CHECK && !process.env.ROLE_CHECK_READ){
        // Default to true if no role checks are specified
        // @ts-ignore
        token.role_valid = true;
        // @ts-ignore
        token.write_privilege = true;
      }
    } else {
      // If roleValue is not available, set privileges to false
      // @ts-ignore
      token.role_valid = false;
      // @ts-ignore
      token.write_privilege = false;
    }

      return token;
    },
    session({ session, token }) {
      // @ts-ignore
      if (token.roleValue) {
        // @ts-ignore
        session.user.roleValue = token.roleValue;
        // @ts-ignore
        session.user.role_valid = token.role_valid;
        // @ts-ignore
        session.user.write_privilege = token.write_privilege;
      }
      return session;
    },
  },
};
