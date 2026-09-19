import Image from "next/image";

export interface EvidenceImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
}

/** Static evidence figure (SHAP/UMAP plots) — responsive width, intrinsic aspect ratio preserved. */
export default function EvidenceImage({ src, alt, width, height }: EvidenceImageProps) {
  return (
    <Image
      className="evidence"
      src={src}
      alt={alt}
      width={width}
      height={height}
      sizes="(max-width: 700px) 100vw, 560px"
    />
  );
}
