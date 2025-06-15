/* eslint-disable @typescript-eslint/no-explicit-any */
import ArticleMeta from "@/components/articles/article-meta";
import { Accordion, AccordionDetails } from "@/components/Accordion";
//import articleMockData from "../../mock-article/article.json";
//import { ArticleType } from "@/utils/types";
import { formatDate, hexToAudioUrl } from "@/utils/function";
import ReactMarkdown from "react-markdown";
//import topicSources from "../../mock-article/topics.json";
import Link from "next/link";
import { useFetchArticleDetails } from "./hooks";

interface Props {
	articleId: string;
}

const Article: React.FC<Props> = ({ articleId }) => {
	const { data } = useFetchArticleDetails(articleId);
	//const article = articleMockData as ArticleType;
	//const sources = topicSources.processed_feeds;

	return (
		<section className="flex justify-center items-center  mt-5">
			<div className="min-w-[800px] min-h-full bg-[#F8F9FA] rounded-sm shadow-md flex flex-col gap-5 p-5">
				<ArticleMeta
					version={data?.article?.version?.toString()}
					createdAt={formatDate(data?.article?.created_at ?? "")}
					updatedAt={formatDate(data?.article?.updated_at ?? "")}
					source={data?.article?.source_feed?.url ?? ""}
					AccessedAt={formatDate(data?.article?.source_feed?.accessed_at ?? "")}
				/>
				{data?.article && (
					<Accordion>
						{data?.article.representations?.map((item: any, index: number) => {
							if (item.type === "kokoro-tts/af_kore:1.2") {
								return (
									<AccordionDetails
										key={index}
										title="Af Kore:1.2"
										subtitle={formatDate(item.created_at)}
									>
										<audio controls className="w-full mt-2 mb-2">
											<source
												src={hexToAudioUrl(item.content)}
												type="audio/mpeg"
											/>
											Your browser does not support the audio element.
										</audio>
									</AccordionDetails>
								);
							} else {
								return (
									<AccordionDetails
										key={index}
										title={item.type}
										subtitle={formatDate(item.created_at)}
									>
										<div className="max-w-[700px] markdown-body">
											<ReactMarkdown>{item.content}</ReactMarkdown>
										</div>
									</AccordionDetails>
								);
							}
						})}
						{/* <AccordionDetails title="Content" subtitle="(17/04/2025, 11:56:09)">
						<p>Summary content or text goes here…</p>
					</AccordionDetails> */}

						{/* <AccordionDetails
						title="En US-amy-medium"
						subtitle="(17/04/2025, 11:56:25)"
					>
						<p>Podcast or alternate content here…</p>
					</AccordionDetails> */}
					</Accordion>
				)}

				<div className="markdown-body max-w-[800px]">
					<ReactMarkdown>{data?.article?.content}</ReactMarkdown>
				</div>
				{data?.sources && data?.sources?.length > 0 ? (
					<div className="article-sources">
						<h4>Sources</h4>
						<ul>
							{data?.sources &&
								data?.sources.map((source, index) => (
									<li key={index} className="mt-0 mb-4 list-disc ml-[30px]">
										<Link
											href={source?.url}
											className="text-blue-600 hover:underline"
										>
											{source.url}
										</Link>{" "}
										({formatDate(source.accessed_at)})
									</li>
								))}
						</ul>
					</div>
				) : (
					"<></>"
				)}
			</div>
		</section>
	);
};
export default Article;
