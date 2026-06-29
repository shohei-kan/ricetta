type PlaceholderPageProps = {
  title: string
  description: string
}

export function PlaceholderPage({ description, title }: PlaceholderPageProps) {
  return (
    <div className="mx-auto max-w-5xl px-5 py-6 md:px-7 md:py-8">
      <p className="text-sm font-bold text-[#c76738]">Ricetta</p>
      <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
        {title}
      </h1>
      <div className="mt-6 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 shadow-sm">
        <p className="text-lg font-semibold text-[#3c3027]">準備中</p>
        <p className="mt-2 text-[#75685e]">{description}</p>
      </div>
    </div>
  )
}
