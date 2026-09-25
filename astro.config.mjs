// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { satteri } from '@astrojs/markdown-satteri';
import starlightOpenAPI, { createOpenAPISidebarGroup } from 'starlight-openapi';

// Páginas de referencia generadas desde public/openapi.json (el mismo archivo se puede descargar).
const referencia = createOpenAPISidebarGroup();

// Mismos ids de encabezado que generaba mkdocs (toc.slugify): sin tildes.
// Así siguen funcionando los #anclas enlazados desde afuera. Igual que en paquete-apertura-datos.
const mkdocsSlugs = () => {
	const seen = new Map();
	return {
		name: 'mkdocs-slugs',
		element: {
			filter: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
			visit(node, ctx) {
				if (typeof node.properties?.id === 'string') return;
				let id = ctx.textContent(node).normalize('NFKD').replace(/[^\x00-\x7F]/g, '')
					.replace(/[^\w\s-]/g, '').trim().toLowerCase().replace(/[-\s]+/g, '-');
				const k = seen.get(id) ?? 0;
				seen.set(id, k + 1);
				ctx.setProperty(node, 'id', k ? `${id}_${k}` : id);
			},
		},
	};
};

const base = '/series-tiempo-ar-api';

export default defineConfig({
	site: 'https://datosgobar.github.io',
	base,
	trailingSlash: 'ignore',
	markdown: { processor: satteri({ hastPlugins: [mkdocsSlugs] }) },
	// El visor Swagger se reemplazó por la referencia generada.
	redirects: { '/open_api/': `${base}/referencia/` },
	integrations: [
		starlight({
			plugins: [starlightOpenAPI([{ base: 'referencia', schema: './public/openapi.json', sidebar: { label: 'Todos los endpoints', group: referencia, operations: { badges: true, labels: 'path' } } }])],
			title: 'API de Series de Tiempo',
			favicon: '/favicon.png',
			description: 'Documentación de la API de Series de Tiempo de la República Argentina.',
			defaultLocale: 'root',
			locales: { root: { label: 'Español', lang: 'es' } },
			customCss: ['./src/styles/datos.css', './src/styles/hub.css'],
			components: { Header: './src/components/Cabecera.astro' },
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/datosgobar/series-tiempo-ar-api' }],
			editLink: { baseUrl: 'https://github.com/datosgobar/series-tiempo-ar-api/edit/master/' },
			head: [
				{ tag: 'link', attrs: { rel: 'preconnect', href: 'https://fonts.googleapis.com' } },
				{ tag: 'link', attrs: { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true } },
				{ tag: 'link', attrs: { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap' } },
			],
			// Mismo menú que el nav de mkdocs.yml.
			sidebar: [
				{ label: 'Inicio', link: '/' },
				{
					label: 'Usuarios',
					items: [
						{ label: 'Comenzar a usar la API', slug: 'quick-start' },
						{ label: 'Filtrar y transformar las series', slug: 'additional-parameters' },
						{ label: 'Integrar la API en planillas de cálculo', slug: 'spreadsheet-integration' },
						{ label: 'Usar en Python', slug: 'python-usage' },
						{ label: 'Usar en componentes web', slug: 'js-usage' },
						{ label: 'Descargar la base completa', slug: 'dumps' },
						{
							label: 'Referencia API',
							items: [
								{ label: '/series', slug: 'reference/api-reference' },
								{ label: '/search', slug: 'reference/search-reference' },
								{ label: '/dump', slug: 'dumps' },
								{ label: '/validate', slug: 'reference/validate' },
								referencia,
							],
						},
						{ label: 'Condiciones de uso', slug: 'terms' },
					],
				},
				{ label: 'Aplicaciones', slug: 'applications' },
				{
					label: 'Publicadores',
					items: [
						{ label: 'Publicar series en la API', slug: 'publishers/quick_start' },
						{ label: 'Generar identificadores', slug: 'publishers/identifiers' },
						{ label: 'Generar descripciones', slug: 'publishers/descriptions' },
					],
				},
				{
					label: 'Desarrolladores',
					items: [
						{ label: 'Arquitectura', slug: 'developers/arquitectura' },
						{ label: 'Instalación', slug: 'developers/development' },
						{ label: 'Administración', slug: 'developers/admin' },
					],
				},
				{ label: 'Historial de versiones', slug: 'history' },
			],
		}),
	],
});
