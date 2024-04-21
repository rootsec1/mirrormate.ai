// Import the GoogleGenerativeAI class from the @google/generative-ai package
import { GoogleGenerativeAI } from "@google/generative-ai";

// Create a new instance of the GoogleGenerativeAI class, passing in the API key from the environment variables
const genAI = new GoogleGenerativeAI(process.env.REACT_APP_GEMINI_API_KEY);

/**
 * Generate content using the Language Learning Model (LLM).
 *
 * @param {string} prompt - The prompt to generate content from.
 * @returns {Promise<string>} The generated content.
 */
export async function promptLLM(prompt) {
  // Get the generative model named "gemini-pro"
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });
  // Generate content from the prompt
  const result = await model.generateContent(prompt);
  // Wait for the response to be available
  const response = await result.response;
  // Get the text from the response
  const text = response.text();
  // Return the text, trimmed of any leading or trailing whitespace
  return text.trim();
}