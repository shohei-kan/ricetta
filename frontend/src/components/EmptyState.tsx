type EmptyStateProps = {
  description: string
  imageSrc: string
  title: string
  compact?: boolean
}

export function EmptyState({
  compact = false,
  description,
  imageSrc,
  title,
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center text-center sm:flex-row sm:text-left ${
        compact ? 'gap-4' : 'gap-5 sm:gap-7'
      }`}
    >
      <img
        alt=""
        aria-hidden="true"
        className={`pointer-events-none shrink-0 select-none object-contain opacity-90 ${
          compact
            ? 'h-20 w-20 sm:h-24 sm:w-24'
            : 'h-36 w-36 sm:h-48 sm:w-48'
        }`}
        src={imageSrc}
      />
      <div>
        <p className="text-lg font-bold text-[#34291f]">{title}</p>
        <p className="mt-2 leading-7 text-[#75685e]">{description}</p>
      </div>
    </div>
  )
}
