type PlaceholderPageProps = {
  title: string
  description: string
}

export function PlaceholderPage({ description, title }: PlaceholderPageProps) {
  return (
    <div className="mx-auto max-w-5xl px-5 py-6 md:px-7 md:py-8">
      <p className="text-sm font-semibold tracking-[0.14em] text-[#9b6b43]">RICETTA</p>
      <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
        {title}
      </h1>
      <div className="mt-6 rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 shadow-sm">
        <p className="text-lg font-semibold text-[#3c3027]">準備中</p>
        <p className="mt-2 text-[#75685e]">{description}</p>
      </div>
    </div>
  )
}
