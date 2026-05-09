'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Tabs } from '@/components/ui/Controls';
import { BookOpen, Lightbulb, History, Code, ChevronDown, ExternalLink } from 'lucide-react';
import { GLOSSARY_TERMS } from '@/lib/constants';

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'thistlethwaite', label: 'Thistlethwaite' },
  { id: 'kociemba', label: 'Kociemba' },
  { id: 'korf', label: 'Korf IDA*' },
  { id: 'glossary', label: 'Glossary' },
];

function ExpandableSection({ title, children, defaultOpen = false }: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details className="group" open={defaultOpen}>
      <summary className="cursor-pointer flex items-center justify-between p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 list-none">
        <span className="font-medium">{title}</span>
        <ChevronDown className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
      </summary>
      <div className="mt-2 p-4 bg-slate-800/30 rounded-lg">
        {children}
      </div>
    </details>
  );
}

function PhaseCard({ number, title, description, moves, fromGroup, toGroup }: {
  number: number;
  title: string;
  description: string;
  moves?: string;
  fromGroup?: string;
  toGroup?: string;
}) {
  return (
    <div className="p-4 border border-slate-700 rounded-lg">
      <div className="flex items-center gap-3 mb-2">
        <span className="w-8 h-8 flex items-center justify-center bg-blue-600 rounded-full text-sm font-bold">
          {number}
        </span>
        <h4 className="font-bold">{title}</h4>
      </div>
      {(fromGroup || toGroup) && (
        <div className="text-sm text-slate-400 mb-2">
          {fromGroup} → {toGroup}
        </div>
      )}
      <p className="text-sm text-slate-300 mb-2">{description}</p>
      {moves && (
        <div className="text-xs text-slate-500">
          Allowed moves: <code className="text-blue-400">{moves}</code>
        </div>
      )}
    </div>
  );
}

export default function EducationalPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">Educational Mode</span>
        </h1>
        <p className="text-slate-400">Learn how each algorithm works</p>
        <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-100">
          This educational page mixes explanatory content with synthetic preview context. Use the thesis artifacts for citation, benchmark claims, and live solver outputs.
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-8 overflow-x-auto">
        <Tabs
          tabs={tabs}
          activeTab={activeTab}
          onChange={setActiveTab}
        />
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <Lightbulb className="w-6 h-6 text-yellow-400" />
              <h2 className="text-xl font-bold">The Rubik's Cube Problem</h2>
            </div>
            <p className="text-slate-300 mb-4">
              The Rubik's Cube has approximately <strong className="text-blue-400">43 quintillion</strong> (43×10¹⁸)
              possible configurations. Finding the optimal solution from any state is a challenging computational problem.
            </p>
            <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <h3 className="font-bold text-purple-400 mb-2">God's Number: 20</h3>
              <p className="text-sm text-slate-300">
                In 2010, it was proven that any Rubik's Cube can be solved in at most 20 moves (in half-turn metric).
                This is known as "God's Number" - the diameter of the Cayley graph of the Rubik's Cube group.
              </p>
            </div>
          </Card>

          <Card>
            <h2 className="text-xl font-bold mb-4">Quick Comparison</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400">Feature</th>
                    <th className="text-center py-3 px-4 text-yellow-400">⚡ Thistlethwaite</th>
                    <th className="text-center py-3 px-4 text-blue-400">🚀 Kociemba</th>
                    <th className="text-center py-3 px-4 text-purple-400">🐢 Korf IDA*</th>
                  </tr>
                </thead>
                <tbody className="text-slate-300">
                  <tr className="border-b border-slate-700/50">
                    <td className="py-3 px-4">Year</td>
                    <td className="text-center py-3 px-4">1981</td>
                    <td className="text-center py-3 px-4">1992</td>
                    <td className="text-center py-3 px-4">1997</td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-3 px-4">Approach</td>
                    <td className="text-center py-3 px-4">Group Theory</td>
                    <td className="text-center py-3 px-4">Two-Phase IDA*</td>
                    <td className="text-center py-3 px-4">Pattern Databases</td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-3 px-4">Phases</td>
                    <td className="text-center py-3 px-4">4</td>
                    <td className="text-center py-3 px-4">2</td>
                    <td className="text-center py-3 px-4">1</td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-3 px-4">Max Moves</td>
                    <td className="text-center py-3 px-4">52</td>
                    <td className="text-center py-3 px-4">Near-optimal</td>
                    <td className="text-center py-3 px-4">Optimal when solved</td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-3 px-4">Optimal?</td>
                    <td className="text-center py-3 px-4">No</td>
                    <td className="text-center py-3 px-4">Near-optimal</td>
                    <td className="text-center py-3 px-4">Exact when solved</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4">Memory</td>
                    <td className="text-center py-3 px-4">Low</td>
                    <td className="text-center py-3 px-4">Medium</td>
                    <td className="text-center py-3 px-4">High</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="mt-4 text-sm text-slate-400">
              Repository benchmark summary: pure Thistlethwaite solved 100/100 test cases, Kociemba also solved
              100/100 with the best practical balance, and the exact Korf backend solved 97/100 within the enforced
              120 second limit.
            </p>
          </Card>

          <Card>
            <div className="flex items-center gap-3 mb-4">
              <History className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold">Historical Timeline</h2>
            </div>
            <div className="space-y-4">
              {[
                { year: '1974', event: 'Ernő Rubik invents the Rubik\'s Cube', color: 'green' },
                { year: '1981', event: 'Thistlethwaite proves 52-move upper bound', color: 'yellow' },
                { year: '1992', event: 'Kociemba introduces Two-Phase Algorithm', color: 'blue' },
                { year: '1997', event: 'Korf uses pattern databases for optimal solving', color: 'purple' },
                { year: '2010', event: 'God\'s Number proven to be 20', color: 'red' },
                { year: '2026', event: 'This thesis project! 🎓', color: 'green' },
              ].map((item, index) => (
                <div key={index} className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-mono bg-${item.color}-500/20 text-${item.color}-400`}>
                    {item.year}
                  </span>
                  <span className="text-slate-300">{item.event}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Thistlethwaite Tab */}
      {activeTab === 'thistlethwaite' && (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">⚡</span>
              <div>
                <h2 className="text-xl font-bold text-yellow-400">Thistlethwaite's Algorithm</h2>
                <p className="text-slate-400">1981 • Group Theory Approach</p>
              </div>
            </div>
            <p className="text-slate-300 mb-4">
              Morwen Thistlethwaite developed a four-phase algorithm based on group theory.
              The key insight is to progressively restrict the set of allowed moves while
              reducing the cube to simpler subgroups.
            </p>
          </Card>

          <Card>
            <h3 className="text-lg font-bold mb-4">The Four Phases</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <PhaseCard
                number={1}
                title="Orient Edges"
                description="Fix edge orientation so all edges can be solved without F/B moves"
                moves="All moves"
                fromGroup="G₀ (all states)"
                toGroup="G₁ (edges oriented)"
              />
              <PhaseCard
                number={2}
                title="Orient Corners + Position M-slice"
                description="Orient corners and position middle layer edges"
                moves="L, R, U, D, F2, B2"
                fromGroup="G₁"
                toGroup="G₂"
              />
              <PhaseCard
                number={3}
                title="Position Corners + E-slice"
                description="Place corners in correct orbits and position E-slice edges"
                moves="L2, R2, U, D, F2, B2"
                fromGroup="G₂"
                toGroup="G₃"
              />
              <PhaseCard
                number={4}
                title="Solve"
                description="Solve the remaining cube using only half turns"
                moves="L2, R2, U2, D2, F2, B2"
                fromGroup="G₃"
                toGroup="Identity (solved)"
              />
            </div>
          </Card>

          <Card>
            <ExpandableSection title="How Group Theory Applies" defaultOpen>
              <p className="text-slate-300 mb-4">
                The Rubik's Cube forms a mathematical group under the operation of move composition.
                Thistlethwaite's insight was to identify a chain of nested subgroups:
              </p>
              <code className="block p-4 bg-slate-900 rounded-lg text-blue-400 text-center mb-4">
                G₀ ⊃ G₁ ⊃ G₂ ⊃ G₃ ⊃ G₄ (identity)
              </code>
              <p className="text-slate-300">
                Each phase reduces the cube from one subgroup to the next by restricting
                which moves are allowed. This dramatically reduces the search space at each step.
              </p>
            </ExpandableSection>
          </Card>

          <Card>
            <h3 className="text-lg font-bold mb-4">Pros & Cons</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-green-400 font-medium mb-2">✅ Advantages</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Pure 4-phase solver with predictable behavior</li>
                  <li>• Low memory requirements</li>
                  <li>• 100% success on the thesis benchmark corpus</li>
                  <li>• Easy to implement lookup tables</li>
                </ul>
              </div>
              <div>
                <h4 className="text-red-400 font-medium mb-2">❌ Disadvantages</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Longer solutions than Kociemba or Korf</li>
                  <li>• Solutions are longer than necessary</li>
                  <li>• Fixed phases may miss shortcuts</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Kociemba Tab */}
      {activeTab === 'kociemba' && (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🚀</span>
              <div>
                <h2 className="text-xl font-bold text-blue-400">Kociemba's Two-Phase Algorithm</h2>
                <p className="text-slate-400">1992 • IDA* Search</p>
              </div>
            </div>
            <p className="text-slate-300 mb-4">
              Herbert Kociemba improved on Thistlethwaite by reducing from 4 phases to 2 and
              using IDA* search within each phase. This produces near-optimal solutions
              and delivered the best overall practical trade-off in the thesis benchmark.
            </p>
          </Card>

          <Card>
            <h3 className="text-lg font-bold mb-4">The Two Phases</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <PhaseCard
                number={1}
                title="Reach G₁ Subgroup"
                description="Orient all edges and corners, position middle-layer edges correctly"
                moves="All moves (R, L, U, D, F, B)"
                fromGroup="G₀ (any state)"
                toGroup="G₁ (half-turn group)"
              />
              <PhaseCard
                number={2}
                title="Solve from G₁"
                description="Solve the cube using only half-turns (except U and D)"
                moves="R2, L2, U, D, F2, B2"
                fromGroup="G₁"
                toGroup="Solved"
              />
            </div>
          </Card>

          <Card>
            <ExpandableSection title="Coordinate Representation" defaultOpen>
              <p className="text-slate-300 mb-4">
                Kociemba encodes the cube state using three coordinates for each phase:
              </p>
              <div className="space-y-3">
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <span className="text-blue-400 font-medium">Phase 1 Coordinates:</span>
                  <ul className="mt-2 text-sm text-slate-300 space-y-1">
                    <li>• Edge orientation (2¹¹ = 2,048 states)</li>
                    <li>• Corner orientation (3⁷ = 2,187 states)</li>
                    <li>• UD-slice edge positions (12C4 = 495 states)</li>
                  </ul>
                </div>
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <span className="text-purple-400 font-medium">Phase 2 Coordinates:</span>
                  <ul className="mt-2 text-sm text-slate-300 space-y-1">
                    <li>• Corner permutation (8! = 40,320 states)</li>
                    <li>• UD-edge permutation (8! = 40,320 states)</li>
                    <li>• UD-slice edge permutation (4! = 24 states)</li>
                  </ul>
                </div>
              </div>
            </ExpandableSection>
          </Card>

          <Card>
            <ExpandableSection title="IDA* Search Algorithm">
              <p className="text-slate-300 mb-4">
                IDA* (Iterative Deepening A*) combines the memory efficiency of depth-first search
                with the optimality of A* search:
              </p>
              <ol className="space-y-3 text-sm text-slate-300">
                <li className="flex gap-3">
                  <span className="text-blue-400">1.</span>
                  <span>Start with a threshold equal to the heuristic estimate</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-blue-400">2.</span>
                  <span>Do depth-first search, pruning branches that exceed the threshold</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-blue-400">3.</span>
                  <span>If no solution found, increase threshold to minimum exceeded value</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-blue-400">4.</span>
                  <span>Repeat until solution is found</span>
                </li>
              </ol>
            </ExpandableSection>
          </Card>

          <Card>
            <h3 className="text-lg font-bold mb-4">Pros & Cons</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-green-400 font-medium mb-2">✅ Advantages</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Near-optimal solutions with strong practical performance</li>
                  <li>• Good balance of speed and quality</li>
                  <li>• Widely used in speedcubing software</li>
                  <li>• Reasonable memory requirements</li>
                </ul>
              </div>
              <div>
                <h4 className="text-red-400 font-medium mb-2">❌ Disadvantages</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Not guaranteed optimal</li>
                  <li>• Phase 1 solution may not lead to best Phase 2</li>
                  <li>• Slower than Thistlethwaite</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Korf Tab */}
      {activeTab === 'korf' && (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🐢</span>
              <div>
                <h2 className="text-xl font-bold text-purple-400">Korf's IDA* with Pattern Databases</h2>
                <p className="text-slate-400">1997 • Optimal Solving</p>
              </div>
            </div>
            <p className="text-slate-300 mb-4">
              Richard Korf developed an optimal solver using admissible pattern databases as heuristics.
              In this repository, the publishable benchmark path uses an external exact backend.
              That path is exact on completed runs, but hard instances can still time out under
              a fixed runtime budget.
            </p>
          </Card>

          <Card>
            <ExpandableSection title="What are Pattern Databases?" defaultOpen>
              <p className="text-slate-300 mb-4">
                A pattern database is a lookup table storing the exact number of moves needed
                to solve a partial goal. For the Rubik's Cube, common patterns include:
              </p>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-700/50 rounded-lg text-center">
                  <div className="text-2xl mb-2">🔲</div>
                  <div className="font-medium">Corner Database</div>
                  <div className="text-sm text-slate-400">8! × 3⁷ states</div>
                  <div className="text-xs text-purple-400">~88 million entries</div>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-lg text-center">
                  <div className="text-2xl mb-2">➖</div>
                  <div className="font-medium">Edge Database 1</div>
                  <div className="text-sm text-slate-400">6 edges subset</div>
                  <div className="text-xs text-purple-400">~42 million entries</div>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-lg text-center">
                  <div className="text-2xl mb-2">➖</div>
                  <div className="font-medium">Edge Database 2</div>
                  <div className="text-sm text-slate-400">Other 6 edges</div>
                  <div className="text-xs text-purple-400">~42 million entries</div>
                </div>
              </div>
            </ExpandableSection>
          </Card>

          <Card>
            <ExpandableSection title="Composite Heuristic">
              <p className="text-slate-300 mb-4">
                The repository also contains a lightweight composite heuristic for exploratory work:
              </p>
              <code className="block p-4 bg-slate-900 rounded-lg text-green-400 text-center mb-4">
                h(state) = max(corner_db[state], edge_db1[state], edge_db2[state])
              </code>
              <p className="text-slate-300">
                This is useful as a practical estimate, but the thesis does not treat every
                lightweight heuristic path in the repository as generally admissible. The exact
                optimality claims are reserved for the external benchmark backend.
              </p>
            </ExpandableSection>
          </Card>

          <Card>
            <ExpandableSection title="Why IDA* for Optimal Solving?">
              <p className="text-slate-300 mb-4">
                IDA* is ideal for optimal solving because:
              </p>
              <ul className="space-y-3 text-sm text-slate-300">
                <li className="flex gap-3">
                  <span className="text-purple-400">•</span>
                  <span><strong>Memory efficient:</strong> O(d) space where d is solution depth</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-purple-400">•</span>
                  <span><strong>Optimal:</strong> Guaranteed to find the shortest solution when paired with an admissible heuristic</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-purple-400">•</span>
                  <span><strong>Anytime:</strong> Can report best solution found so far</span>
                </li>
              </ul>
            </ExpandableSection>
          </Card>

          <Card>
            <h3 className="text-lg font-bold mb-4">Pros & Cons</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-green-400 font-medium mb-2">✅ Advantages</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Exact optimality on completed runs</li>
                  <li>• Shortest solutions among the compared solvers</li>
                  <li>• Memory-efficient search</li>
                  <li>• Theoretically beautiful</li>
                </ul>
              </div>
              <div>
                <h4 className="text-red-400 font-medium mb-2">❌ Disadvantages</h4>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• Slow for difficult scrambles</li>
                  <li>• Hard requested scramble length 20 cases can time out under a fixed budget</li>
                  <li>• Large pattern database storage</li>
                  <li>• Long preprocessing time</li>
                  <li>• Variable execution time</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Glossary Tab */}
      {activeTab === 'glossary' && (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center gap-3 mb-6">
              <BookOpen className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold">Glossary of Terms</h2>
            </div>
            <div className="grid gap-4">
              {GLOSSARY_TERMS.map((item, index) => (
                <div
                  key={index}
                  className="p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors"
                >
                  <h3 className="font-bold text-blue-400 mb-1">{item.term}</h3>
                  <p className="text-sm text-slate-300">{item.definition}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="text-xl font-bold mb-4">References</h2>
            <div className="space-y-3">
              {[
                {
                  title: 'Thistlethwaite\'s 52-Move Algorithm',
                  author: 'Morwen Thistlethwaite, 1981',
                  url: 'https://www.jaapsch.net/puzzles/thistle.htm',
                },
                {
                  title: 'Two-Phase Algorithm',
                  author: 'Herbert Kociemba, 1992',
                  url: 'http://kociemba.org/cube.htm',
                },
                {
                  title: 'Finding Optimal Solutions to Rubik\'s Cube',
                  author: 'Richard E. Korf, 1997',
                  url: 'https://www.aaai.org/Papers/AAAI/1997/AAAI97-109.pdf',
                },
                {
                  title: 'God\'s Number is 20',
                  author: 'Rokicki et al., 2010',
                  url: 'http://www.cube20.org/',
                },
              ].map((ref, index) => (
                <a
                  key={index}
                  href={ref.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors group"
                >
                  <div>
                    <div className="font-medium group-hover:text-blue-400 transition-colors">
                      {ref.title}
                    </div>
                    <div className="text-sm text-slate-400">{ref.author}</div>
                  </div>
                  <ExternalLink className="w-4 h-4 text-slate-500 group-hover:text-blue-400" />
                </a>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
