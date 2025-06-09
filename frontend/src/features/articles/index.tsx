import ArticleMeta from "@/components/articles/article-meta";
import { Accordion, AccordionDetails } from "@/components/Accordion";
import articleMockData from "../../mock-article/article.json";
import { ArticleType } from "@/utils/types";

const Article: React.FC = () => {
	const article = articleMockData as ArticleType;
	console.log(article);

	return (
		<section className="flex justify-center items-center h-screen mt-5">
			<div className="min-w-[800px] min-h-full bg-[#F8F9FA] rounded-sm shadow-md flex flex-col gap-5 p-5">
				<ArticleMeta
					version="13"
					createdAt="11/04/2025, 01:43:30"
					updatedAt="17/04/2025, 11:56:09"
					source=" https://eindhovennews.com/news/2025/04/politicians-do-not-want-housing-construction-on-welschap/"
					AccessedAt="17/04/2025, 11:42:43"
				/>

				<Accordion>
					<AccordionDetails
						title="Radio-transcript"
						subtitle="(17/04/2025, 11:56:20)"
					>
						<p>
							Eindhoven&apos;s housing market is getting a boost. The city
							council has approved a plan...
						</p>
						<audio controls className="w-full mt-2">
							<source src="/example.mp3" type="audio/mpeg" />
							Your browser does not support the audio element.
						</audio>
					</AccordionDetails>

					<AccordionDetails title="Content" subtitle="(17/04/2025, 11:56:09)">
						<p>Summary content or text goes here…</p>
					</AccordionDetails>

					<AccordionDetails
						title="En US-amy-medium"
						subtitle="(17/04/2025, 11:56:25)"
					>
						<p>Podcast or alternate content here…</p>
					</AccordionDetails>
				</Accordion>
			</div>
		</section>
	);
};
export default Article;
