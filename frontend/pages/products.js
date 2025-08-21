import Head from 'next/head';

export async function getServerSideProps() {
  try {
    const res = await fetch('http://localhost:3001/products');
    const products = await res.json();
    return { props: { products } };
  } catch {
    return { props: { products: [] } };
  }
}

export default function Products({ products }) {
  return (
    <>
      <Head>
        <title>Tienda KX</title>
      </Head>
      <main className="product-grid">
        {products.map((p) => (
          <div className="product-card" key={p.id}>
            <h2>{p.name}</h2>
            <p>${'{'}p.price{'}'}</p>
          </div>
        ))}
      </main>
    </>
  );
}
