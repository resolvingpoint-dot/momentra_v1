import { initializeApp, getApps, type FirebaseApp } from "firebase/app";
import {
  getAuth,
  type Auth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  EmailAuthProvider,
  reauthenticateWithCredential,
  updatePassword,
  updateProfile,
  signOut as firebaseSignOut,
  type User,
} from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

let app: FirebaseApp | undefined;
let auth: Auth | undefined;

export function getFirebaseApp(): FirebaseApp {
  if (!app) {
    app = getApps().length > 0 ? getApps()[0] : initializeApp(firebaseConfig);
  }
  return app;
}

export function getFirebaseAuth(): Auth {
  if (!auth) {
    auth = getAuth(getFirebaseApp());
  }
  return auth;
}

export async function signInWithEmail(email: string, password: string): Promise<User> {
  const result = await signInWithEmailAndPassword(
    getFirebaseAuth(),
    email.toLowerCase(),
    password,
  );
  return result.user;
}

export async function registerWithEmail(email: string, password: string): Promise<User> {
  const result = await createUserWithEmailAndPassword(
    getFirebaseAuth(),
    email.toLowerCase(),
    password,
  );
  return result.user;
}

export async function signInWithGoogle(): Promise<User> {
  const provider = new GoogleAuthProvider();
  const result = await signInWithPopup(getFirebaseAuth(), provider);
  return result.user;
}

export async function getFirebaseIdToken(user: User): Promise<string> {
  return user.getIdToken();
}

export async function signOutFirebase(): Promise<void> {
  await firebaseSignOut(getFirebaseAuth());
}

export function isEmailPasswordUser(user: User | null | undefined): boolean {
  return user?.providerData.some((p) => p.providerId === "password") ?? false;
}

export async function updateFirebaseDisplayName(displayName: string): Promise<void> {
  const user = getFirebaseAuth().currentUser;
  if (!user) throw new Error("Not signed in");
  await updateProfile(user, { displayName: displayName.trim() });
}

export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<void> {
  const user = getFirebaseAuth().currentUser;
  if (!user?.email) throw new Error("Not signed in with email");
  const credential = EmailAuthProvider.credential(user.email, currentPassword);
  await reauthenticateWithCredential(user, credential);
  await updatePassword(user, newPassword);
}
