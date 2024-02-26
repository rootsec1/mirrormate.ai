import React, { useRef } from "react";

import { useScroll, useTransform } from "framer-motion";
import { GeminiWithTypewriterEffect } from "../components/ui/gemini-with-typewriter-effect";

export default function SplashPage() {
  const ref = useRef(null);

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const pathLengthFirst = useTransform(scrollYProgress, [0, 0.8], [0.2, 1.2]);
  const pathLengthSecond = useTransform(scrollYProgress, [0, 0.8], [0.15, 1.2]);
  const pathLengthThird = useTransform(scrollYProgress, [0, 0.8], [0.1, 1.2]);
  const pathLengthFourth = useTransform(scrollYProgress, [0, 0.8], [0.05, 1.2]);
  const pathLengthFifth = useTransform(scrollYProgress, [0, 0.8], [0, 1.2]);

  function onGetStartedButtonClick() {
    console.log("Get Started button clicked");
  }

  return (
    <div style={{ height: "100%" }}>
      <div
        className="h-[400vh] bg-black w-full dark:border dark:border-white/[0.1] rounded-md relative pt-40 overflow-clip"
        ref={ref}
      >
        <GeminiWithTypewriterEffect
          title={"mirrormate.ai ♔"}
          description={"   Outplay your Rival"}
          buttonText={"Get Started"}
          buttonOnClick={onGetStartedButtonClick}
          pathLengths={[
            pathLengthFirst,
            pathLengthSecond,
            pathLengthThird,
            pathLengthFourth,
            pathLengthFifth,
          ]}
        />
      </div>
    </div>
  );
}
