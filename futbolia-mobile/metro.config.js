// Metro configuration for FutbolIA
// https://docs.expo.dev/guides/monorepos/
const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// Suppress non-critical React Native Web deprecation warnings
const originalWarn = console.warn;
console.warn = function (...args) {
  if (
    typeof args[0] === "string" &&
    args[0].includes("pointerEvents is deprecated")
  ) {
    return;
  }
  originalWarn.apply(console, args);
};

