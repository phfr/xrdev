import{gh as m,gf as g}from"./index-CE8xIjrv.js";const a="https://pubchem.ncbi.nlm.nih.gov/rest/pug";function t(o){return o.replace(/[&<>"']/g,e=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[e])}function u(o,e=6){const s=o.title.toLowerCase(),i=[];for(const n of o.synonyms){if(i.length>=e)break;n.toLowerCase()===s||n.length>40||/^(C\d{5}|CHEBI:\d+|HMDB\d+|\d+-\d+-\d+|[A-Z0-9]{8,}|.*\d{4,}.*)$/.test(n)||i.push(n)}return i}function b(o){if(!o.substanceClass)return o.compound?p(o.compound):"";const e=o.compound?`
      <div style="margin-top: 10px; padding: 6px 8px; border: 1px dashed #666; border-radius: 6px;">
        <div style="font-size: 11px; color: #e8b84a; margin-bottom: 6px;">Example compound of this class (found by name, not the class itself):</div>
        ${p(o.compound,{exampleOf:o.substanceClass})}
      </div>`:'<div style="margin-top: 8px; font-size: 12px; color: #999;">No example compound found.</div>';return f(o.substanceClass)+e}function r(o,e){return`<a href="${t(o)}" target="_blank" rel="noopener" style="color:#7fc8ff;text-decoration:none;">${t(e)}</a>`}function f(o){const[e,...s]=o.names,i=e?e.charAt(0).toUpperCase()+e.slice(1):o.keggId;return`
    <div style="border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 8px;">
      <div style="font-weight: 700; font-size: 16px; color: #00ffff; margin-bottom: 4px;">${t(i)}
        <span style="font-size: 11px; font-weight: 600; color: #000; background: #e8b84a; border-radius: 999px; padding: 1px 8px; margin-left: 6px; vertical-align: 2px;">substance class</span>
      </div>
      ${s.length?`<div style="font-size: 11px; color: #999;">${t(s.slice(0,6).join(", "))}</div>`:""}
    </div>
    <div style="color: #ddd; font-size: 12px; line-height: 1.45; margin-bottom: 8px;">
      KEGG ${t(o.keggId)} stands for a class of compounds with a generic structure (for example
      varying fatty acid chains), not a single molecule. PubChem has no single structure for it.
    </div>
    <div style="font-size: 11px; color: #aaa; border-top: 1px solid #333; padding-top: 6px;">
      ${r(`https://www.kegg.jp/entry/${o.keggId}`,`KEGG ${o.keggId}`)} &middot;
      ${r(`https://pubchem.ncbi.nlm.nih.gov/substance/${o.sid}`,`PubChem substance ${o.sid}`)}
    </div>`}function p(o,e={}){const s=[r(`https://pubchem.ncbi.nlm.nih.gov/compound/${o.cid}`,`PubChem ${o.cid}`),o.keggId&&!e.exampleOf?r(`https://www.kegg.jp/entry/${o.keggId}`,`KEGG ${o.keggId}`):"",o.hmdbId?r(`https://hmdb.ca/metabolites/${o.hmdbId}`,o.hmdbId):"",o.chebiId?r(`https://www.ebi.ac.uk/chebi/searchId.do?chebiId=${o.chebiId}`,o.chebiId):""].filter(Boolean).join(" &middot; "),i=[["Formula",o.formula],["Molecular weight",o.molecularWeight?`${o.molecularWeight} g/mol`:void 0],["IUPAC name",o.iupacName],["InChIKey",o.inchiKey]],n=u(o),c=m(g.pubchemPng(o.cid))??`${a}/compound/cid/${o.cid}/PNG?image_size=220x220`;return`
    <div style="border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 8px;">
      <div style="font-weight: 700; font-size: 16px; color: #00ffff; margin-bottom: 4px;">${t(o.title)}</div>
      ${n.length?`<div style="font-size: 11px; color: #999;">${t(n.join(", "))}</div>`:""}
    </div>
    <div style="display: flex; gap: 12px; align-items: flex-start; margin-bottom: 8px;">
      <img crossorigin="anonymous" src="${t(c)}" alt="Structure of ${t(o.title)}"
        style="width: 160px; height: 160px; flex-shrink: 0; background: #fff; border-radius: 6px;"
        onerror="this.style.display='none'"/>
      <div style="display: grid; grid-template-columns: auto 1fr; gap: 3px 10px; font-size: 12px; min-width: 0;">
        ${i.filter(([,d])=>d).map(([d,l])=>`<div style="color: #aaa;">${d}</div><div style="color: #fff; word-break: break-word;">${t(l)}</div>`).join("")}
      </div>
    </div>
    ${o.description?`
      <div style="color: #ddd; font-size: 12px; line-height: 1.45; margin-bottom: 8px;">${t(o.description.text)}
        ${o.description.source?`<span style="color: #888;">(${t(o.description.source)})</span>`:""}
      </div>`:""}
    <div style="font-size: 11px; color: #aaa; border-top: 1px solid #333; padding-top: 6px;">${s}</div>
  `}export{b as formatPubChemTooltip};
