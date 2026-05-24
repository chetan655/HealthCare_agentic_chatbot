// // In development, we use an empty string so requests go through the Vite proxy (preventing CORS errors).
// // In production, we use the VITE_API_URL directly.
// const API_BASE = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_URL || '');

// export async function sendMessage(question, threadId, lat, long, imageFile) {
//   const formData = new FormData();
//   formData.append('question', question);
//   formData.append('thread_id', threadId);
//   formData.append('lat', lat);
//   formData.append('long', long);

//   if (imageFile) {
//     formData.append('image', imageFile);
//   }

//   const response = await fetch(`${API_BASE}/chat`, {
//     method: 'POST',
//     body: formData,
//   });

//   if (!response.ok) {
//     throw new Error(`Server error: ${response.status}`);
//   }

//   return response;
// }

// export function getLocation() {
//   return new Promise((resolve) => {
//     if (!navigator.geolocation) {
//       resolve({ lat: '29.9478', long: '76.8170' });
//       return;
//     }

//     navigator.geolocation.getCurrentPosition(
//       (position) => {
//         resolve({
//           lat: String(position.coords.latitude),
//           long: String(position.coords.longitude),
//         });
//       },
//       () => {
//         resolve({ lat: '29.9478', long: '76.8170' });
//       },
//       { timeout: 8000, maximumAge: 300000 }
//     );
//   });
// }

// export function inferAgent(question, hasImage) {
//   if (hasImage) return 'ocr';
//   const q = question.toLowerCase();
//   const hospitalKeywords = ['hospital', 'nearby', 'clinic', 'medical center', 'emergency center', 'find hospital', 'nearest', 'close to me'];
//   if (hospitalKeywords.some((kw) => q.includes(kw))) return 'hospital';
//   return 'general';
// }

// In development, we use an empty string so requests go through the Vite proxy (preventing CORS errors).
// In production, we use the VITE_API_URL directly.
const API_BASE = import.meta.env.DEV ? "" : import.meta.env.VITE_API_URL || "";

// Fail fast if env missing in production (prevents silent bugs)
if (!import.meta.env.DEV && !API_BASE) {
  throw new Error("VITE_API_URL is not defined");
}

export async function sendMessage(question, threadId, userId, lat, long, imageFile) {
  const formData = new FormData();
  formData.append("question", question);
  formData.append("thread_id", threadId);
  formData.append("user_id", userId);
  formData.append("lat", lat);
  formData.append("long", long);

  if (imageFile) {
    formData.append("image", imageFile);
  }

  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Server error: ${response.status} - ${text}`);
  }

  return response;
}

export function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({ lat: "29.9478", long: "76.8170" });
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: String(position.coords.latitude),
          long: String(position.coords.longitude),
        });
      },
      () => {
        resolve({ lat: "29.9478", long: "76.8170" });
      },
      { timeout: 8000, maximumAge: 300000 },
    );
  });
}

export function inferAgent(question, hasImage) {
  if (hasImage) return "ocr";
  const q = question.toLowerCase();
  const hospitalKeywords = [
    "hospital",
    "nearby",
    "clinic",
    "medical center",
    "emergency center",
    "find hospital",
    "nearest",
    "close to me",
  ];
  if (hospitalKeywords.some((kw) => q.includes(kw))) return "hospital";
  return "general";
}

export async function getChatHistory(threadId) {
  const response = await fetch(`${API_BASE}/chat/history?thread_id=${threadId}&limit=50`);
  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }
  return response.json();
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    let errorMsg = "Login failed";
    try {
      const text = await response.text();
      if (text) {
        const errorData = JSON.parse(text);
        errorMsg = errorData.detail || errorMsg;
      }
    } catch (e) {
      // Ignored
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export async function signupUser(email, full_name, password) {
  const response = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, full_name, password }),
  });

  if (!response.ok) {
    let errorMsg = "Signup failed";
    try {
      const text = await response.text();
      if (text) {
        const errorData = JSON.parse(text);
        errorMsg = errorData.detail || errorMsg;
      }
    } catch (e) {
      // Ignored
    }
    throw new Error(errorMsg);
  }

  return response.json();
}
