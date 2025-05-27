interface ArticleMetaProps {
	version?: string;
	createdAt?: string;
	updatedAt?: string;
	source?: string;
	AccessedAt?: string;
}

const ArticleMeta: React.FC<ArticleMetaProps> = ({
	version,
	createdAt,
	updatedAt,
	source,
	AccessedAt,
}) => {
	return (
		<div className="flex flex-col gap-1 text-sm text-[#666]">
			{version && (
				<div className="flex">
					<span className="font-medium">Version:</span>
					<span className="ml-1">{version}</span>
				</div>
			)}
			{createdAt && (
				<div className="flex">
					<span className="font-medium">Created:</span>
					<span className="ml-1">{createdAt}</span>
				</div>
			)}
			{updatedAt && (
				<div className="flex">
					<span className="font-medium">Updated:</span>
					<span className="ml-1">{updatedAt}</span>
				</div>
			)}
			{source && (
				<div className="flex mt-2">
					<span className="font-medium">Source:</span>
					<a
						href={source}
						target="_blank"
						rel="noopener noreferrer"
						className="ml-1 text-blue-600 hover:underline break-all"
					>
						{source}
					</a>
				</div>
			)}
			{AccessedAt && (
				<div className="flex">
					<span className="font-medium">Accessed:</span>
					<span className="ml-1">{AccessedAt}</span>
				</div>
			)}
		</div>
	);
};

export default ArticleMeta;
