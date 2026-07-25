import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, deleteDoc, doc, getDocs, query, where } from "firebase/firestore";
import { getAuth, signInAnonymously } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

signInAnonymously(auth).catch(console.error);

export { db, auth };

export type ItineraryItem = {
  id: string;
  type: "attraction" | "restaurant";
  name: string;
  category?: string;
  location?: string;
  price?: string;
  memo?: string;
  googleMapsLink?: string;
  createdAt: number;
};

export async function addItem(item: Omit<ItineraryItem, "id" | "createdAt">) {
  const docRef = await addDoc(collection(db, "itinerary"), {
    ...item,
    createdAt: Date.now(),
  });
  return docRef.id;
}

export async function getItems() {
  const snapshot = await getDocs(collection(db, "itinerary"));
  return snapshot.docs.map((doc) => ({
    ...doc.data(),
    id: doc.id,
  })) as ItineraryItem[];
}

export async function deleteItem(id: string) {
  await deleteDoc(doc(db, "itinerary", id));
}
